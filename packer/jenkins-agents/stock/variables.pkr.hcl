variable "aws_access_key" {  
  type = string
}

variable "aws_secret_key" {
  type = string
}

variable "image_prefix" {
}

variable "source_image_family" {
}

variable "docker_cache_images" {
  description = "Images to preload; keep aligned with TIRX docker-images.ini."
  type        = list(string)
  default = [
    "tlcpack/ci-manylinux-cuda13-1@sha256:659a10db9a04b286b2c02113e081709d7273c38e7a8fd148c8b7ebe7df2be64c"
  ]
}
