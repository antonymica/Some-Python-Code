import subprocess
import os
import shlex
import sys

# Configuration générale
ISO_PATH = os.path.abspath("ubuntu-22.04.5-live-server-amd64.iso")
VM_BASE_NAME = "UbuntuServer"
VM_COUNT = 2
RAM_SIZE = 2048  # en MB
CPU_COUNT = 1
DISK_SIZE_MB = 25000  # en Mo
VM_FOLDER = os.path.expanduser("~/VirtualBox VMs")

def run(cmd):
    """Exécute une commande shell avec gestion d’erreur."""
    print(f"[+] Executing: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Erreur lors de l'exécution de : {cmd}")
        print(f"    → Code retour : {e.returncode}")
        sys.exit(1)

def create_vm(index):
    """Crée et configure une VM VirtualBox."""
    vm_name = f"{VM_BASE_NAME}-{index}"
    vm_path = os.path.join(VM_FOLDER, vm_name)
    disk_path = os.path.join(vm_path, f"{vm_name}.vdi")

    # Créer la VM
    run(f"VBoxManage createvm --name {shlex.quote(vm_name)} --register")

    # Configurer la RAM, CPU, OS type
    run(f"VBoxManage modifyvm {shlex.quote(vm_name)} --memory {RAM_SIZE} --cpus {CPU_COUNT} --ostype Ubuntu_64")

    # Créer le disque virtuel
    os.makedirs(vm_path, exist_ok=True)
    run(f"VBoxManage createmedium disk --filename {shlex.quote(disk_path)} --size {DISK_SIZE_MB} --format VDI")

    # Ajouter un contrôleur SATA pour le disque
    run(f"VBoxManage storagectl {shlex.quote(vm_name)} --name 'SATA Controller' --add sata --controller IntelAHCI")
    run(f"VBoxManage storageattach {shlex.quote(vm_name)} --storagectl 'SATA Controller' --port 0 --device 0 --type hdd --medium {shlex.quote(disk_path)}")

    # Ajouter un contrôleur IDE pour le lecteur ISO
    run(f"VBoxManage storagectl {shlex.quote(vm_name)} --name 'IDE Controller' --add ide")
    run(f"VBoxManage storageattach {shlex.quote(vm_name)} --storagectl 'IDE Controller' --port 0 --device 0 --type dvddrive --medium {shlex.quote(ISO_PATH)}")

    # Configuration du boot
    run(f"VBoxManage modifyvm {shlex.quote(vm_name)} --boot1 dvd --boot2 disk --boot3 none --boot4 none")

    # Réseau NAT par défaut
    run(f"VBoxManage modifyvm {shlex.quote(vm_name)} --nic1 nat")

    # Lancement de la VM en arrière-plan
    run(f"VBoxManage startvm {shlex.quote(vm_name)} --type headless")

if __name__ == "__main__":
    # Vérifie que l'ISO existe
    if not os.path.isfile(ISO_PATH):
        print(f"[!] Fichier ISO introuvable : {ISO_PATH}")
        sys.exit(1)

    # Crée les VMs
    for i in range(1, VM_COUNT + 1):
        create_vm(i)
    print("[+] Toutes les VMs ont été créées et démarrées.")
    print("[+] Vous pouvez les gérer via VirtualBox.")
