import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

export interface ContainerSecrets {
    name: pulumi.Input<string>;
    parameter: pulumi.Input<string>;
}

export interface ServiceProps {
    vpcId: pulumi.Input<string>

    cluster: pulumi.Input<string>;
    environment?: pulumi.Input<pulumi.Input<aws.ecs.KeyValuePair[]>>;
    secrets: ContainerSecrets[];

    command?: pulumi.Input<string[]>;
    imageTag?: pulumi.Input<string>;
    containerPort: pulumi.Input<number>;
    containerCpu?: pulumi.Input<string>;
    containerMemory?: pulumi.Input<string>;

    deploymentController?: pulumi.Input<string>;

    desiredCount?: pulumi.Input<number>;
    role?: pulumi.Input<string>;
}

export class Service extends pulumi.ComponentResource {
    constructor (
        name: string,
        props: ServiceProps,
        opts?: pulumi.ComponentResourceOptions,
    ) {

        super("decodingml:main:Service", name, {}, opts);

        const accountId = pulumi.output(aws.getCallerIdentity()).accountId;
        const region = pulumi.output(aws.getRegion()).name;

        const imageUrl = pulumi.interpolate`${accountId}.dkr.ecr.${region}.amazonaws.com/chamberlain:latest`

        const containerSecrets =  props.secrets.map(secret => {
            return {
              name: secret.name,
              valueFrom: pulumi.interpolate`arn:aws:ssm:${region}:${accountId}:parameter/${secret.parameter}`
            } as aws.ecs.Secret;
        })

        const logGroup = new aws.cloudwatch.LogGroup(`log-group`, {
            name: `/ecs/${props.cluster}/${name}`,
            retentionInDays: 90,
            tags: {
                Name: `${props.cluster}-${name}-cluster-log-group`
            }
        })

        const taskDefinition = new aws.ecs.TaskDefinition(`${name}-ecs-task-definition`, {
            family: name,
            networkMode: 'awsvpc',
            requiresCompatibilities: ["FARGATE"],
            cpu: props.containerCpu || "512",
            memory: props.containerMemory || "1024",
            executionRoleArn: pulumi.output(aws.iam.getRole({name: `ecs-task-execution-role`})).arn,
            taskRoleArn: props.role,
            containerDefinitions: pulumi
                .all([imageUrl, props.logGroup, props.environment, containerSecrets])
                .apply(([image,logGroup,environment, secrets]) =>
                    JSON.stringify([{
                        name: name,
                        image: image,
                        portMappings: [{
                            containerPort: props.containerPort,
                        }],
                        command: props.command,
                        environment: environment,
                        secrets: secrets,
                        logConfiguration: {
                            logDriver: "awslogs",
                            options: {
                                "awslogs-group": logGroup,
                                "awslogs-create-group": "true",
                                "awslogs-region": "eu-central-1",
                                "awslogs-stream-prefix": name,
                            },
                        },
                    } as aws.ecs.ContainerDefinition])
                )
        }, {parent: this})

        const serviceDiscovery = new aws.servicediscovery.Service(`${name}-service-discovery`, {
            name: name,
            description: `Service discovery for ${name}`,
            dnsConfig: {
                routingPolicy: "MULTIVALUE",
                dnsRecords: [{ type: "A", ttl: 60 }],
                namespaceId: pulumi.output(aws.servicediscovery.getDnsNamespace({
                    name: `streaming.internal`,
                    type: 'DNS_PRIVATE',
                })).id,
            },
            healthCheckCustomConfig: {
                failureThreshold: 1
            },
        }, {parent: this})

        new aws.ecs.Service(`${name}-ecs-service`, {
            name: `${name}-service`,
            cluster: props.cluster,
            launchType: 'FARGATE',
            deploymentController: {
                type: props.deploymentController || "ECS",
            },
            desiredCount: props.desiredCount || 1,
            taskDefinition: taskDefinition.arn,
            serviceRegistries: {
                registryArn: serviceDiscovery.arn,
                containerName: `${name}`,
            },
            networkConfiguration: {
                assignPublicIp: false,
                securityGroups: pulumi.output(aws.ec2.getSecurityGroups({
                    tags: {Name: `ecs-host-sg`}
                })).ids,
                subnets: pulumi.output(aws.ec2.getSubnets({tags: {Type: 'private'}})).ids
            }
        }, {parent: this})
    }
}