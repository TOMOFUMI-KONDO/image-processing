//resource "aws_autoscaling_group" "main" {
//  name                = "${var.project}-autoscaling-group"
//  max_size            = 3
//  min_size            = 1
//  desired_capacity    = 1
//  vpc_zone_identifier = [aws_subnet.public_a.id, aws_subnet.public_c.id]
//  health_check_type   = "EC2"
//
//
//  launch_template {
//    id      = aws_launch_template.main.id
//    version = "$Latest"
//  }
//
//  tags = concat(
//    [
//      {
//        key                 = "Name"
//        value               = "${var.project}-autoscaling-group"
//        propagate_at_launch = false
//      },
//      {
//        key                 = "Project"
//        value               = var.project
//        propagate_at_launch = false
//      }
//    ]
//  )
//}
//
//resource "aws_launch_template" "main" {
//  name                   = "${var.project}-launch-template"
//  image_id               = var.ami.amazon-linux-2-ecs
//  instance_type          = "t3.nano"
//  key_name               = var.key_pair
//  vpc_security_group_ids = [aws_security_group.public_instance.id]
//  user_data              = filebase64("userdata.sh")
//
//  iam_instance_profile {
//    name = aws_iam_instance_profile.main.name
//  }
//
//  tag_specifications {
//    resource_type = "instance"
//
//    tags = {
//      Name    = "${var.project}-ec2"
//      Project = var.project
//    }
//  }
//
//  tags = {
//    Name    = "${var.project}-launch-template"
//    Project = var.project
//  }
//}
//
resource "aws_iam_instance_profile" "main" {
  name = "${var.project}-iam-instance-profile"
  role = aws_iam_role.instance-iam-role.name

  tags = {
    Project = var.project
  }
}

resource "aws_iam_role" "instance-iam-role" {
  name = "${var.project}-instance-iam-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = {
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Sid    = "",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }
  })

  tags = {
    project = var.project
  }
}

resource "aws_iam_role_policy_attachment" "AmazonEC2ContainerServiceforEC2Role" {
  role       = aws_iam_role.instance-iam-role.name
  policy_arn = data.aws_iam_policy.AmazonEC2ContainerServiceforEC2Role.arn
}

data "aws_iam_policy" "AmazonEC2ContainerServiceforEC2Role" {
  name = "AmazonEC2ContainerServiceforEC2Role"
}