# Deploy ssh key for instance access
resource "aws_key_pair" "deployer" {
  key_name   = terraform.workspace
  public_key = file("~/.ssh/id_rsa.pub")
}
