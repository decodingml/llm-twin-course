import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";


export interface MessageQueueBrokerProps {
    vpcId: pulumi.Input<string>

    engineVersion?: pulumi.Input<string>
    instanceType?: pulumi.Input<string>

}

export class MessageQueueBroker extends pulumi.ComponentResource {

    constructor(
        name: string,
        props: MessageQueueBrokerProps,
        opts?: pulumi.ComponentResourceOptions,
    ) {
        super("decodingml:main:MessageQueueBroker", name, {}, opts);

        const accountId = pulumi.output(aws.getCallerIdentity()).accountId;
        const region = pulumi.output(aws.getRegion()).name;

        const securityGroup =  new aws.ec2.SecurityGroup(`${name}-mq-sg`, {
            name: `${name}-mq-sg`,
            description: "Message Queue broker access",
            vpcId: props.vpcId,
            ingress: [
                {
                    description: "Ingress from AMPQS protocol",
                    fromPort: 5671,
                    toPort: 5671,
                    protocol: "tcp",
                },
                {
                    description: "Ingress from HTTPS protocol",
                    fromPort: 443,
                    toPort: 443,
                    protocol: "tcp",
                },
            ],
            egress: [{
                protocol: "-1",
                description: "Allow all outbound traffic by default",
                fromPort: 0,
                toPort: 0,
                cidrBlocks: ["0.0.0.0/0"],
            }],
            tags: {
                Name: `${name}-mq-sg`
            },
        }, {parent: this})

        const broker = new aws.mq.Broker(`${name}-mq-broker`, {
            brokerName: `${name}-mq-broker`,
            engineType: "RabbitMQ",
            engineVersion: props.engineVersion || "3.11.20",
            hostInstanceType: props.instanceType || "mq.t3.micro",
            securityGroups: [securityGroup.id],
            deploymentMode: "SINGLE_INSTANCE",
            logs: {
                general: true,
            },
            publiclyAccessible: true,
            subnetIds: pulumi.output(aws.ec2.getSubnets({tags: {Type: 'public'}})).ids,
            users: pulumi.all([
                this.getSecretValue(`arn:aws:secretsmanager:${region}:${accountId}:secret:/${name}/broker/admin`),
                this.getSecretValue(`arn:aws:secretsmanager:${region}:${accountId}:secret:/${name}/broker/replication-user`)
            ]).apply(([adminSecret, replicationUserSecret]) => [
                {
                    username: JSON.parse(adminSecret).username,
                    password: JSON.parse(adminSecret).password,
                    consoleAccess: true,
                },
                {
                    username: JSON.parse(replicationUserSecret).username,
                    password: JSON.parse(replicationUserSecret).password,
                    consoleAccess: true,
                    replicationUser: true
                }
            ]),
            tags: {
                Name: `${name}-mq-sg`
            },
        }, {parent: this})

        const hostSSMParameter = new aws.ssm.Parameter(`${name}-mq-broker-host-ssm-parameter`, {
            name: `/${name}/broker/host`,
            type: aws.ssm.ParameterType.String,
            description: `RabbitMQ cluster host for ${name}-mq-broker`,
            value: broker.instances[0].endpoints[0].apply(endpoint => {
                return endpoint.split(":")[0];
            }),
        }, {parent: this})

        const portSSMParameter = new aws.ssm.Parameter(`${name}-mq-broker-port-ssm-parameter`, {
            name: `/${name}/broker/port`,
            type: aws.ssm.ParameterType.String,
            description: `RabbitMQ cluster port for ${name}-mq-broker`,
            value: "5671",
        }, {parent: this})
    }

    private async getSecretValue(secretName: string): Promise<pulumi.Output<string>> {
        return pulumi.output(aws.secretsmanager.getSecretVersion({
                secretId: secretName,
            }, { async: true })).apply(secretVersion => {
                if (!secretVersion.secretString) {
                    throw new Error("Secret version contains no string data");
                }
                return secretVersion.secretString;
            });
    }
}