# infrastructure

该目录用于存放基础设施即代码（IaC）相关的脚本与配置，如Terraform、Pulumi等。

## 技术选型
本项目推荐使用 [Terraform](https://www.terraform.io/) 进行云资源的自动化管理和部署。

## 初始化指引
1. 安装 Terraform（参考官网：https://developer.hashicorp.com/terraform/downloads）
2. 进入本目录：`cd infrastructure`
3. 初始化 Terraform 项目：
   ```sh
   terraform init
   ```
4. 编写和应用资源配置：
   ```sh
   terraform plan
   terraform apply
   ``` 