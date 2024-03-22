import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

export interface CrawlerProps {
    vpcId: pulumi.Input<string>
    timeout: pulumi.Input<number>
    memory: pulumi.Input<number>
}

export class Crawler extends pulumi.ComponentResource {
    public readonly arn: pulumi.Output<string>

    constructor (
        name: string,
        props: CrawlerProps,
        opts?: pulumi.ComponentResourceOptions,
    ) {
        super("decodingml:main:Crawler", name, {}, opts);

        const accountId = pulumi.output(aws.getCallerIdentity()).accountId;
        const region = pulumi.output(aws.getRegion()).name;

        const lambdaExecutionRole = new aws.iam.Role(`${name}-role`, {
            assumeRolePolicy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [{
                    Effect: "Allow",
                    Principal: {
                        Service: "lambda.amazonaws.com",
                    },
                    Action: "sts:AssumeRole",
                }],
            }),
            managedPolicyArns: [
                aws.iam.ManagedPolicy.AmazonS3FullAccess,
                aws.iam.ManagedPolicy.AmazonDocDBFullAccess,
                aws.iam.ManagedPolicy.AWSLambdaBasicExecutionRole,
                aws.iam.ManagedPolicy.AWSLambdaVPCAccessExecutionRole,
                aws.iam.ManagedPolicy.CloudWatchLambdaInsightsExecutionRolePolicy
            ]
        })

        const sg = new aws.ec2.SecurityGroup(`${name}-security-group`, {
            name: `${name}-sg`,
            description: "Crawler Lambda Access",
            vpcId: props.vpcId,
            egress: [{
                protocol: "-1",
                description: "Allow all outbound traffic by default",
                fromPort: 0,
                toPort: 0,
                cidrBlocks: ["0.0.0.0/0"],
            }],
            tags: {
                Name: `${name}-sg`
            }
        })

        const lambdaFunction = new aws.lambda.Function(`${name}-lambda-function`, {
            name: `${name}`,
            imageUri: pulumi.interpolate`${accountId}.dkr.ecr.${region}.amazonaws.com/crawler:latest`,
            packageType: 'Image',
            description: 'Crawler Lambda Function',
            timeout: props.timeout,
            memorySize: props.memory,
            role: lambdaExecutionRole.arn,
            vpcConfig: {
                subnetIds: pulumi.output(aws.ec2.getSubnets({tags: {Type: 'public'}})).ids,
                securityGroupIds: [sg.id],
            }
        }, {dependsOn: lambdaExecutionRole})

        this.arn = lambdaFunction.arn

        this.registerOutputs({
            arn:  this.arn
        })
    }
}
