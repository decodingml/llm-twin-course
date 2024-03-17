import * as pulumi from '@pulumi/pulumi'
import * as aws from '@pulumi/aws'

interface Props {
  vpcId: pulumi.Input<string>
  cidr: string
  az: string
  type: 'public' // | 'private' | 'private-with-nat'
}

export class Subnet extends pulumi.ComponentResource {
  public id: pulumi.Output<string>
  public az: pulumi.Output<string>
  public routeTable: aws.ec2.RouteTable

  private name: string
  private subnet: aws.ec2.Subnet

  private readonly tags = {
    module: 'ai',
    scope: 'networking',
  }

  constructor(
    name: string,
    props: Props,
    opts?: pulumi.ComponentResourceOptions,
  ) {
    super('decodingml:ai:subnet', name, {}, opts)
    this.name = name
    this.az = pulumi.output(props.az)

    const parent = this

    this.subnet = new aws.ec2.Subnet(
      `${this.name}-subnet`,
      {
        vpcId: props.vpcId,
        availabilityZone: props.az,
        cidrBlock: props.cidr,
        tags: {
          ...this.tags,
          Name: name,
        },
        mapPublicIpOnLaunch: props.type === 'public',
        // assignIpv6AddressOnCreation: props.type === 'public',
      },
      { parent },
    )
    this.id = this.subnet.id

    this.routeTable = new aws.ec2.RouteTable(
      `${this.name}-route-table`,
      {
        vpcId: props.vpcId,
      },
      { parent },
    )

    new aws.ec2.RouteTableAssociation(
      `${this.name}-route-table-association`,
      {
        routeTableId: this.routeTable.id,
        subnetId: this.subnet.id,
      },
      { parent },
    )

    this.registerOutputs()
  }

  public addRoute(
    name: string,
    props: Omit<aws.ec2.RouteArgs, 'routeTableId'>,
  ) {
    new aws.ec2.Route(
      `${this.name}-${name}`,
      {
        routeTableId: this.routeTable.id,
        ...props,
      },
      { parent: this },
    )

    return this
  }
}
