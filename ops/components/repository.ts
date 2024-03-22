import * as pulumi from '@pulumi/pulumi'
import * as aws from '@pulumi/aws'

interface Props {}

export class Repository extends pulumi.ComponentResource {
  public name: pulumi.Output<string>
  public arn: pulumi.Output<string>
  public url: pulumi.Output<string>

  public static dockerTags = {
    github: 'github-crawler-latest',
    linkedin: 'linkedin-crawler-latest',
    medium: 'medium-crawler-latest',

  } as const

  private readonly tags = {
    module: 'ai',
    scope: 'ecr',
  }

  constructor(
    name: string,
    props: Props,
    opts?: pulumi.ComponentResourceOptions,
  ) {
    super('deocingml:ai:ecr', name, {}, opts)

    const ecr = new aws.ecr.Repository(
      `${name}-repository`,
      {
        name,
        tags: this.tags,
        imageTagMutability: 'MUTABLE',
      },
      { parent: this },
    )

    new aws.ecr.LifecyclePolicy(
      `${name}-lifecycle-policy`,
      {
        repository: ecr.name,
        policy: {
          rules: [
            {
              action: { type: 'expire' },
              selection: {
                tagStatus: 'untagged',
                countNumber: 30,
                countUnit: 'days',
                countType: 'sinceImagePushed',
              },
              rulePriority: 1,
              description: 'Delete older than 30 days images with no tag.',
            },
          ],
        },
      },
      { parent: this },
    )

    this.arn = ecr.arn
    this.name = ecr.name
    this.url = ecr.repositoryUrl

    this.registerOutputs()
  }
}
