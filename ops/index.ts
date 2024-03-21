import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";
import {Vpc} from "./components/vpc";
import {DocumentDBCluster} from "./components/docdb";
import {Crawler} from "./components/crawler";

const vpc= new Vpc("network-overlay", {})

const docdb = new DocumentDBCluster("warehouse", {
    vpcId: vpc.id,
    instanceClass: "db.t3.medium",
}, {dependsOn: vpc})

const lambda = new Crawler("crawler", {
    vpcId: vpc.id,
    timeout: 900,
    memory: 3008
})

export const VpcID: pulumi.Output<string> = vpc.id
