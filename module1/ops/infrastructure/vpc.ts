import * as pulumi from '@pulumi/pulumi'
import * as aws from '@pulumi/aws'
import { Subnet } from './resources/subnet'

const cidr = (rest: string) => `10.100.${rest}`

interface Props {
  region: string
}

type SubnetGroups = 'webservers' | 'compute'

export class Vpc extends pulumi.ComponentResource {
  public readonly id: aws.ec2.Vpc['id']
  public readonly igw: aws.ec2.InternetGateway
  public readonly subnets: Record<SubnetGroups, Record<'a' | 'b' | 'c', Subnet>>

  private readonly vpc: aws.ec2.Vpc
  private name: string
  private region: string

  private readonly tags = {
    module: 'ai',
    scope: 'networking',
  }

  constructor(
    name: string,
    props: Props,
    opts?: pulumi.ComponentResourceOptions,
  ) {
    super('decodingml:ai:vpc', name, {}, opts)

    this.name = name
    this.region = props.region

    const kms = new aws.kms.Key(
      `${name}-cmk`,
      { tags: this.tags },
      { parent: this },
    )
    new aws.kms.Alias(`${name}-cmk-alias`, {
      targetKeyId: kms.keyId,
      name: 'alias/vpc',
    })

    this.vpc = new aws.ec2.Vpc(
      `${name}-vpc`,
      {
        cidrBlock: cidr('0.0/16'),
        enableNetworkAddressUsageMetrics: true,
        tags: this.tags,
      },
      { parent: this },
    )
    this.id = this.vpc.id

    const flowLogsBucket = new aws.s3.Bucket(
      `${name}.vpc.logs`,
      {
        serverSideEncryptionConfiguration: {
          rule: {
            applyServerSideEncryptionByDefault: {
              kmsMasterKeyId: kms.arn,
              sseAlgorithm: 'aws:kms',
            },
          },
        },
      },
      { parent: this },
    )
    new aws.ec2.FlowLog(
      `${name}-flow-logs`,
      {
        logDestination: flowLogsBucket.arn,
        logDestinationType: 's3',
        trafficType: 'ALL',
        vpcId: this.vpc.id,
      },
      { parent: this },
    )

    this.igw = new aws.ec2.InternetGateway(
      `${name}-igw`,
      {
        tags: this.tags,
        vpcId: this.vpc.id,
      },
      { parent: this },
    )

    const webservers = this.createSubnetGroup('web-servers', {
      cidrList: [cidr('0.0/24'), cidr('1.0/24'), cidr('2.0/24')],
      igw: this.igw,
    })
    const compute = this.createSubnetGroup('compute', {
      cidrList: [cidr('100.0/22'), cidr('104.0/22'), cidr('108.0/22')],
    })

    this.subnets = {
      webservers,
      compute,
    }

    new aws.ec2.VpcEndpoint(
      `${name}-dynamo-endpoint`,
      {
        serviceName: 'com.amazonaws.eu-central-1.dynamodb',
        vpcId: this.vpc.id,
        routeTableIds: this.getSubnetGroup('compute').map(
          subnet => subnet.routeTable.id,
        ),
      },
      { parent: this },
    )
    new aws.ec2.VpcEndpoint(
      `${name}-s3-endpoint`,
      {
        serviceName: 'com.amazonaws.eu-central-1.s3',
        vpcId: this.vpc.id,
        routeTableIds: this.getSubnetGroup('compute').map(
          subnet => subnet.routeTable.id,
        ),
      },
      { parent: this },
    )

    this.createFckNat()

    this.registerOutputs()
  }

  /**
   * Creates subnet groups in all 3 AZs in the region.
   * @see https://nuvibit.com/vpc-subnet-calculator/ for subnetting.
   */
  private createSubnetGroup(
    name: string,
    props: {
      cidrList: [string, string, string]
      igw?: aws.ec2.InternetGateway
    },
  ) {
    const group = {
      a: new Subnet(
        `${name}-a`,
        {
          az: `${this.region}a`,
          cidr: props.cidrList[0],
          type: 'public',
          vpcId: this.vpc.id,
        },
        { parent: this },
      ),
      b: new Subnet(
        `${name}-b`,
        {
          az: `${this.region}b`,
          cidr: props.cidrList[1],
          type: 'public',
          vpcId: this.vpc.id,
        },
        { parent: this },
      ),
      c: new Subnet(
        `${name}-c`,
        {
          az: `${this.region}c`,
          cidr: props.cidrList[2],
          type: 'public',
          vpcId: this.vpc.id,
        },
        { parent: this },
      ),
    }

    if (props.igw) {
      for (const [, subnet] of Object.entries(group)) {
        subnet.addRoute('route-to-igw', {
          gatewayId: props.igw.id,
          destinationCidrBlock: '0.0.0.0/0',
          // destinationIpv6CidrBlock: '::/0',
        })
      }
    }

    return group
  }

  private createFckNat() {
    const sg = new aws.ec2.SecurityGroup(
      `${this.name}-nat-sg`,
      {
        description: 'FckNat Security Group',
        ingress: [
          {
            cidrBlocks: [cidr('0.0/16')],
            protocol: '-1',
            fromPort: 0,
            toPort: 0,
          },
        ],
        egress: [
          { cidrBlocks: ['0.0.0.0/0'], protocol: '-1', fromPort: 0, toPort: 0 },
        ],
        vpcId: this.vpc.id,
      },
      { parent: this },
    )

    const ssmEndpointsSg = new aws.ec2.SecurityGroup(
      `${this.name}-vpc-endpoint-interface-sg`,
      {
        vpcId: this.vpc.id,
        ingress: [
          {
            securityGroups: [sg.id],
            fromPort: 443,
            toPort: 443,
            protocol: 'tcp',
          },
        ],
        egress: [
          {
            cidrBlocks: [cidr('0.0/16')],
            fromPort: 443,
            toPort: 443,
            protocol: 'tcp',
          },
        ],
      },
    )

    const ssmEndpoints = [
      'com.amazonaws.eu-central-1.ssm',
      'com.amazonaws.eu-central-1.ec2',
      'com.amazonaws.eu-central-1.ec2messages',
      'com.amazonaws.eu-central-1.ssmmessages',
      'com.amazonaws.eu-central-1.kms',
      'com.amazonaws.eu-central-1.logs',
    ].forEach((endpoint, i) => {
      const service = endpoint.split('.').pop()
      new aws.ec2.VpcEndpoint(
        `${this.name}-${service}-${service}`,
        {
          serviceName: endpoint,
          vpcId: this.vpc.id,
          vpcEndpointType: 'Interface',
          securityGroupIds: [ssmEndpointsSg.id],
          subnetIds: this.getSubnetGroup('compute').map(subnet => subnet.id),
        },
        { parent: this },
      )
    })

    const eni = new aws.ec2.NetworkInterface(
      `${this.name}-nat-interface`,
      {
        subnetId: this.subnets.webservers.a.id,
        securityGroups: [sg.id],
        sourceDestCheck: false,
      },
      { parent: this },
    )

    const role = new aws.iam.Role(
      `${this.name}-nat-asg-role`,
      {
        assumeRolePolicy: {
          Version: '2012-10-17',
          Statement: [
            {
              Action: ['sts:AssumeRole'],
              Effect: 'Allow',
              Principal: {
                Service: 'ec2.amazonaws.com',
              },
            },
          ],
        },
        managedPolicyArns: [
          `arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore`,
        ],
        inlinePolicies: [
          {
            name: 'for-ec2',
            policy: JSON.stringify({
              Statement: [
                {
                  Action: [
                    'ec2:AttachNetworkInterface',
                    'ec2:ModifyNetworkInterfaceAttribute',
                    'ec2:AssociateAddress',
                    'ec2:DisassociateAddress',
                    'ec2:*',
                  ],
                  Effect: 'Allow',
                  Resource: '*',
                },
              ],
              Version: '2012-10-17',
            } as aws.iam.PolicyDocument),
          },
        ],
      },
      { parent: this },
    )

    const asgProfile = new aws.iam.InstanceProfile(
      `${this.name}-nat-asg-profile`,
      { role },
      { parent: this },
    )

    const launchTemplate = new aws.ec2.LaunchTemplate(
      `${this.name}-launch-template`,
      {
        name: 'fcknat-launch-template',
        imageId: 'ami-04eb0af991f1fe55d',
        instanceType: 't4g.nano',
        iamInstanceProfile: { arn: asgProfile.arn },
        vpcSecurityGroupIds: [sg.id],
        tags: this.tags,
        tagSpecifications: [{ tags: this.tags, resourceType: 'instance' }],
        userData: eni.id.apply(id =>
          Buffer.from(
            [
              '#!/bin/bash',
              `echo "eni_id=${id}" >> /etc/fck-nat.conf`,
              'service fck-nat restart',
            ].join('\n'),
          ).toString('base64'),
        ),
      },
      { dependsOn: [asgProfile], parent: this },
    )

    new aws.autoscaling.Group(
      `${this.name}-asg`,
      {
        maxSize: 1,
        minSize: 1,
        desiredCapacity: 1,
        launchTemplate: {
          id: launchTemplate.id,
          version: '$Latest',
        },
        vpcZoneIdentifiers: [this.subnets.webservers.a.id],
        tags: [{ key: 'Name', value: 'fck-nat', propagateAtLaunch: true }],
      },
      { parent: this },
    )

    this.getSubnetGroup('compute').forEach(subnet => {
      subnet.addRoute('to-nat', {
        destinationCidrBlock: '0.0.0.0/0',
        networkInterfaceId: eni.id,
      })
    })
  }

  public getSubnetGroup(name: SubnetGroups, azs?: Array<'a' | 'b' | 'c'>) {
    return Object.entries(this.subnets[name])
      .map(([az, subnet]) => {
        if (!azs) return subnet
        if (azs.includes(az as (typeof azs)[number])) return subnet
        return []
      })
      .flat()
  }
}
