import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";


export interface ECSClusterProps {
    vpcId: pulumi.Input<string>
}

export class ECSCluster extends pulumi.ComponentResource {
    name: pulumi.Output<string>

    constructor (
        name: string,
        props: ECSClusterProps,
        opts?: pulumi.ComponentResourceOptions,
    ) {
        super("decodingml:main:ECSCluster", name, {}, opts);

        const cluster = new aws.ecs.Cluster(`${name}-cluster`, {
            name: `${name}-cluster`,
        }, {parent: this})

        this.name = cluster.name

        const securityGroup = new aws.ec2.SecurityGroup(`${name}-sg`, {
            name: `${name}-ecs-host-sg`,
            description: 'Access to the ECS hosts that run containers',
            vpcId: props.vpcId,
            ingress: [
                {
                    description: "Ingress from other containers in the same security group",
                    fromPort: 0,
                    toPort: 0,
                    protocol: "-1",
                    self: true,
                }
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
            tags: {
                Name: `${name}-ecs-host-sg`
            }
        }, {parent: this})

        new aws.servicediscovery.PrivateDnsNamespace(`${name}-private-dns-namespace`, {
            name: `${name}.internal`,
            vpc: props.vpcId,
        }, {parent: this})

        this.registerOutputs({
            name: this.name
        })

    }
}