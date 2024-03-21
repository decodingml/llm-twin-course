import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";


export interface DocumentDBClusterProps {
    vpcId: pulumi.Input<string>
    instanceClass?: pulumi.Input<string>
    multiAZ?: pulumi.Input<boolean>
    port?: pulumi.Input<number>

    backupRetentionPeriod?: pulumi.Input<number>
}

export class DocumentDBCluster extends pulumi.ComponentResource {

    constructor (
        name: string,
        props: DocumentDBClusterProps,
        opts?: pulumi.ComponentResourceOptions,
    ) {
        super("decodingml:main:DocumentDBCluster", name, {}, opts);


        const subnetGroup = new aws.docdb.SubnetGroup(`${name}-docdb-subnet-group`, {
            name: `${name}-cluster-subnet-group`,
            description: `VPC subnet group for the ${name}-cluster`,
            subnetIds: pulumi.output(aws.ec2.getSubnets({tags: {Type: 'public'}})).ids,
            tags: {
                Name: `${name}-cluster-subnet-group`
            }
        }, {parent: this})

        const securityGroup = new aws.ec2.SecurityGroup(`${name}-docdb-sg`, {
            name: `${name}-docdb-cluster-sg`,
            description: "Database access",
            vpcId: props.vpcId,
            tags: {
                Name: `${name}-docdb-cluster-sg`
            },
            ingress: [
                {
                    description: "Ingress from anywhere",
                    fromPort: props.port || 27017,
                    toPort: props.port || 27017,
                    protocol: "-1",
                },
            ],
            egress: [{
                protocol: "-1",
                description: "Allow all outbound traffic by default",
                fromPort: 0,
                toPort: 0,
                cidrBlocks: ["0.0.0.0/0"],
            }],
        }, {parent: this})

        const cluster = new aws.docdb.Cluster(`${name}-docdb-cluster`, {
            // availabilityZones:  pulumi.output(aws.getAvailabilityZones({state: "available"}) if props.multiAZ else
            backupRetentionPeriod: props.backupRetentionPeriod || 7,
            clusterIdentifier: `${name}-cluster`,
            masterUsername: pulumi.output(aws.ssm.getParameter({ name: `/${name}/cluster/master/username` })).value,
            masterPassword: pulumi.output(aws.ssm.getParameter({ name: `/${name}/cluster/master/password` })).value,
            engineVersion: "5.0.0",
            port: props.port || 27017,
            dbSubnetGroupName: subnetGroup.name,
            storageEncrypted: true,
            skipFinalSnapshot: true,
            vpcSecurityGroupIds: [ securityGroup.id ],
            tags: {
                Name: `${name}-cluster`
            }
        }, {parent: this})

        const primaryInstance = new aws.docdb.ClusterInstance(`${name}-docdb-primary-instance`, {
            clusterIdentifier: cluster.clusterIdentifier,
            identifier: `${name}-primary-instance`,
            instanceClass: props.instanceClass || "db.t3.medium",
            tags: {
                Name: `${name}-primary-instance`
            }
        }, {parent: this})
    }
}
