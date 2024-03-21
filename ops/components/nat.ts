import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import {SubnetCidrBlocks} from "./config";

export interface NatGatewayProps {
    env: pulumi.Input<string>
    vpcId: pulumi.Input<string>
    subnet: pulumi.Input<string>

    instanceImageAmiId?: pulumi.Input<string>
}

export class NatGateway extends pulumi.ComponentResource {
    public readonly id: pulumi.Output<string>

    constructor(
        name: string,
        props: NatGatewayProps,
        opts?: pulumi.ComponentResourceOptions,
    ) {
        super("decodingml:main:NatGateway", name, {}, opts);

        const config = new pulumi.Config();

        const sg = new aws.ec2.SecurityGroup(`${name}-security-group`, {
            description: "Security Group for NAT Gateway",
            ingress: [
                {
                    cidrBlocks: [SubnetCidrBlocks.VPC],
                    description: "Allow all inbound traffic from network",
                    protocol: "-1",
                    fromPort: 0,
                    toPort: 0,
                },
            ],
            egress: [
                {
                    cidrBlocks: ['0.0.0.0/0'],
                    description: "Allow all outbound traffic by default",
                    protocol: "-1",
                    fromPort: 0,
                    toPort: 0,
                },
            ],
            vpcId: props.vpcId,
        }, {parent: this})

        const iamRole = new aws.iam.Role(`${name}-role`, {
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
                    name: 'for-nat',
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

        }, {parent: this})

        const eni = new aws.ec2.NetworkInterface(`${name}-eni`, {
            subnetId: props.subnet,
            securityGroups: [sg.id],
            sourceDestCheck: false,
        }, {parent: this})

        this.id = eni.id

        const instanceProfile = new aws.iam.InstanceProfile(`${name}-instance-profile`, {
            role: iamRole
        }, {parent: this})

        const launchTemplate = new aws.ec2.LaunchTemplate(`${name}-launch-template`, {
            name: `pi-${props.env}-nat-launch-template`,
            imageId: config.require('natInstanceImageId'),
            instanceType: 't4g.nano',
            iamInstanceProfile: { arn: instanceProfile.arn },
            vpcSecurityGroupIds: [ sg.id ],
            userData: eni.id.apply(id =>
              Buffer.from(
                [
                  '#!/bin/bash',
                  `echo "eni_id=${id}" >> /etc/fck-nat.conf`,
                  'service fck-nat restart',
                ].join('\n'),
              ).toString('base64'),
            ),
            tags: {
                Name: `pi-${props.env}-nat-launch-template`
            },
            tagSpecifications: [{
                tags: {
                    Name: `pi-${props.env}-nat-launch-template`
                },
                resourceType: 'instance'
            }]
        }, {dependsOn: instanceProfile, parent: this})


        new aws.autoscaling.Group(`${name}-autoscaling-group`, {
            maxSize: 1,
            minSize: 1,
            desiredCapacity: 1,
            launchTemplate: {
              id: launchTemplate.id,
              version: '$Latest',
            },
            vpcZoneIdentifiers: [ props.subnet ],
            tags: [{ key: 'Name', value: `pi-${props.env}-nat-instance-launch-template`, propagateAtLaunch: true }]
        }, {parent: this})

        this.registerOutputs({
            id: this.id,
        })
    }
}