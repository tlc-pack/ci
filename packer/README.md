# ci-packer

Builds AMIs for Jenkins workers.

## Docker cache

`jenkins-agents/stock/variables.pkr.hcl` lists the images to preload on x86-64
and ARM workers. Keep the digest aligned with TIRX's `docker-images.ini`.
GPU AMIs inherit the x86-64 cache. The separate EXTRA image is not cached.

Stopped `ci-ami-cache-*` containers protect cached layers from cleanup.
Keep these containers and the cache-aware hourly cleanup in place.
ECR pulls still fetch metadata but reuse matching local layers.

## Rollout

1. Merge to `main` and wait for the `packer` workflow to succeed, or start it
   manually. It builds and registers the AMIs in `us-west-2`.
2. Review the Terraform plan, then run **terraform apply** to update worker
   launch templates. Packer does not trigger this automatically.
3. Verify cache reuse and CI timings on a newly launched worker. Existing
   workers keep their old AMIs.

Run local tests with:

```bash
python3 -m unittest discover -s packer/tests -v
```

These tests mock Docker. Real image pulls, cleanup, and AMI boot still require
integration testing. The workflow runs Packer validation before each build.
