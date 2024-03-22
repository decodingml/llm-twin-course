import * as pulumi from '@pulumi/pulumi'
import * as aws from '@pulumi/aws'
import {SubnetCidrBlocks} from "./config";

interface VpcProps {}

export class Vpc extends pulumi.ComponentResource {
    public readonly id: pulumi.Output<string>

    constructor(
        name: string,
        props: VpcProps,
        opts?: pulumi.ComponentResourceOptions,
    ) {
        super("decodingml:main:Vpc", name, {}, opts);

        const vpc = new aws.ec2.Vpc(`${name}-vpc`, {
            cidrBlock: SubnetCidrBlocks.VPC,
            enableDnsSupport: true,
            enableDnsHostnames: true,
            tags: {
                Name: `${name}-vpc`,
            },
        }, { parent: this });

        this.id = vpc.id

        const azs = aws.getAvailabilityZones({
            state: "available"
        })

        const publicSubnetOne = new aws.ec2.Subnet(`${name}-public-subnet-one`, {
            vpcId: vpc.id,
            availabilityZone: azs.then(azs => azs.names?.[0]),
            cidrBlock: SubnetCidrBlocks.PublicOne,
            mapPublicIpOnLaunch: true,
            tags: {
                Name: `${name}-public-subnet-one`,
                Type: 'public',
            }
        }, {parent: this})

        const publicSubnetTwo = new aws.ec2.Subnet(`${name}-public-subnet-two`, {
            vpcId: vpc.id,
            availabilityZone: azs.then(azs => azs.names?.[1]),
            cidrBlock: SubnetCidrBlocks.PublicTwo,
            mapPublicIpOnLaunch: true,
            tags: {
                Name: `${name}-public-subnet-two`,
                Type: 'public',
            }
        }, {parent: this})

                // Setup networking resources for the public subnets.
        const internetGateway= new aws.ec2.InternetGateway(`${name}-internet-gateway`, {
            vpcId: vpc.id,
            tags: {
                Name: `${name}-internet-gateway`
            }
        }, {parent: this})

        const publicRouteTable = new aws.ec2.RouteTable(`${name}-public-route-table`, {
            vpcId: vpc.id,
            tags: {
                Name: `${name}-public-route-table`
            }
        }, {parent: this})

        new aws.ec2.Route(`${name}-public-route`, {
            routeTableId: publicRouteTable.id,
            destinationCidrBlock: "0.0.0.0/0",
            gatewayId: internetGateway.id
        }, {parent: this})

        new aws.ec2.RouteTableAssociation(`${name}-public-subnet-one-rta`, {
            subnetId: publicSubnetOne.id,
            routeTableId: publicRouteTable.id
        }, {parent: this})
        new aws.ec2.RouteTableAssociation(`${name}-public-subnet-two-rta`, {
            subnetId: publicSubnetTwo.id,
            routeTableId: publicRouteTable.id,
        }, {parent: this})

    }
}
