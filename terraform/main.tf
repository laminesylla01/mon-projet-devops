terraform {
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
    }
  }
}

# Connexion à Proxmox (via pve3)
provider "proxmox" {
  endpoint  = "https://192.168.1.20:8006/"
  api_token = var.proxmox_api_token
  insecure  = true   # certificat auto-signé de Proxmox
}

# Le CT de recette
resource "proxmox_virtual_environment_container" "debtest01" {
  node_name    = "pve3"
  description  = "CT de recette - géré par Terraform"
  unprivileged = true

  features {
    nesting = true   # nécessaire pour Docker
  }

  initialization {
    hostname = "debtest01"

    ip_config {
      ipv4 {
        address = "192.168.1.93/24"
        gateway = var.gateway
      }
    }

    user_account {
      keys = [trimspace(file(var.ssh_public_key))]
    }
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  operating_system {
    template_file_id = "local:vztmpl/debian-13-standard_13.1-2_amd64.tar.zst"
    type             = "debian"
  }

  disk {
    datastore_id = var.storage
    size         = 8
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 1024
  }
}
