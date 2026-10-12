variable "proxmox_api_token" {
  description = "Jeton API Proxmox (format user@realm!id=secret)"
  type        = string
  sensitive   = true
}

variable "gateway" {
  description = "Passerelle IPv4 du réseau"
  type        = string
}

variable "storage" {
  description = "Stockage Proxmox pour le disque du CT"
  type        = string
  default     = "local-lvm"
}

variable "ssh_public_key" {
  description = "Clé publique SSH autorisée sur le CT (pour Ansible)"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}
