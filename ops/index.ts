import * as pulumi from "@pulumi/pulumi";
import {Vpc} from "./components/vpc";
import {DocumentDBCluster} from "./components/docdb";
import {Crawler} from "./components/crawler";
import {MessageQueueBroker} from "./components/mq";
import {Service} from "./components/ecs/service";
import {ECSCluster} from "./components/ecs/cluster";

const vpc= new Vpc("network-overlay", {})

const docdb = new DocumentDBCluster("warehouse", {
    vpcId: vpc.id,
    instanceClass: "db.t3.medium",
}, {dependsOn: vpc})

const lambda = new Crawler("crawler", {
    vpcId: vpc.id,
    timeout: 900,
    memory: 3008
}, {dependsOn: docdb})

const mq = new MessageQueueBroker("mq", {
    vpcId: vpc.id,
}, {dependsOn: lambda})

const cluster = new ECSCluster("streaming", {
    vpcId: vpc.id
})

const bytewaxWorker = new Service("bytewax-worker", {
    vpcId: vpc.id,
    cluster: cluster.name,
    containerPort: 9000,
    secrets: [
        {
            name: "MONGO_DATABASE_HOST",
            parameter: "database/host",
        },
        {
            name: "OPENAI_API_KEY",
            parameter: "database/host",
        },
        {
            name: "QDRANT_DATABASE_HOST",
            parameter: "database/username",
        },
        {
            name: "QDRANT_DATABASE_PORT",
            parameter: "database/host",
        },
        {
            name: "QDRANT_APIKEY",
            parameter: "database/username",
        },
        {
            name: "RABBITMQ_HOST",
            parameter: "database/host",
        },
        {
            name: "RABBITMQ_PORT",
            parameter: "database/username",
        },
        {
            name: "RABBITMQ_DEFAULT_USERNAME",
            parameter: "database/host",
        },
        {
            name: "RABBITMQ_DEFAULT_PASSWORD",
            parameter: "database/username",
        },
    ]
})

const cdc = new Service("cdc", {
    vpcId: vpc.id,
    cluster: cluster.name,
    containerPort: 9000,
    secrets: [
        {
            name: "MONGO_DATABASE_HOST",
            parameter: "database/host",
        },
        {
            name: "RABBITMQ_HOST",
            parameter: "database/host",
        },
        {
            name: "RABBITMQ_PORT",
            parameter: "database/username",
        },
        {
            name: "RABBITMQ_DEFAULT_USERNAME",
            parameter: "database/host",
        },
        {
            name: "RABBITMQ_DEFAULT_PASSWORD",
            parameter: "database/username",
        },
    ]
})


export const VpcID: pulumi.Output<string> = vpc.id
