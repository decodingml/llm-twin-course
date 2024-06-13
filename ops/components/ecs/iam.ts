import * as aws from "@pulumi/aws";


export const ecsRole = new aws.iam.Role("ecs-role", {
    name: `ecs-role`,
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "ecs.amazonaws.com" }),
    path: "/",
    inlinePolicies: [{
        name: "ecs-service",
        policy: JSON.stringify({
            Statement: [{
                Action: [
                    'ec2:AttachNetworkInterface',
                    'ec2:CreateNetworkInterface',
                    'ec2:CreateNetworkInterfacePermission',
                    'ec2:DeleteNetworkInterface',
                    'ec2:DeleteNetworkInterfacePermission',
                    'ec2:Describe*',
                    'ec2:DetachNetworkInterface',
                    'elasticloadbalancing:DeregisterInstancesFromLoadBalancer',
                    'elasticloadbalancing:DeregisterTargets',
                    'elasticloadbalancing:Describe*',
                    'elasticloadbalancing:RegisterInstancesWithLoadBalancer',
                    'elasticloadbalancing:RegisterTargets'
                ],
                Effect: 'Allow',
                Resource: '*'
            }],
            Version: '2012-10-17',
        } as aws.iam.PolicyDocument)
    }]
})


export const ecsTaskExecutionRole = new aws.iam.Role("ecs-task-execution-role", {
    name: `ecs-task-execution-role`,
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "ecs-tasks.amazonaws.com" }),
    path: "/",
    inlinePolicies: [
        {
            name: "ecs-logs",
            policy: JSON.stringify({
                Statement: [{
                    Action: [
                        'logs:CreateLogGroup'
                    ],
                    Effect: 'Allow',
                    Resource: '*'
                }]
            } as aws.iam.PolicyDocument),
        },
        {
            name: "ecs-ssm",
            policy: JSON.stringify({
                Statement: [{
                    Sid: "readEnvironmentParameters",
                    Action: [
                        'ssm:GetParameters'
                    ],
                    Effect: 'Allow',
                    Resource: "*"
                }]
            } as aws.iam.PolicyDocument),
        }
    ],
    managedPolicyArns: [
        'arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
    ]
})