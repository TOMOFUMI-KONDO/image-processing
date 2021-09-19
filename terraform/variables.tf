variable "project" {
  type = string
}

variable "domain" {
  type = map(string)
  default = {
    apex  = ""
    front = ""
    api   = ""
  }
}

variable "vercel_record" {
  type = map(string)
  default = {
    a     = ""
    cname = ""
  }
}

variable "profile" {
  type = string
}

variable "my_global_ip" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "subnet_cidr" {
  type = map(string)

  default = {
    public_a  = "",
    public_c  = "",
    private_a = "",
    private_c = ""
  }
}

variable "cidr_default_gateway" {
  type = map(string)
  default = {
    ipv4 = "0.0.0.0/0"
    ipv6 = "::/0"
  }
}

variable "az" {
  type = map(string)

  default = {
    az_a = "ap-northeast-1a"
    az_c = "ap-northeast-1c"
    az_d = "ap-northeast-1d"
  }
}

variable "container_image_uri" {
  type = map(any)
  default = {
    app   = ""
    nginx = ""
  }
}

variable "s3_bucket" {
  type = string
}

variable "key_pair" {
  type = string
}

variable "ami" {
  type = map(string)

  default = {
    amazon-linux-2     = "ami-06098fd00463352b6"
    amazon-linux-2-ecs = "ami-0822fa1ed6836019b"
  }
}
