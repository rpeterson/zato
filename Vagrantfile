VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "ubuntu/trusty64"
  
  config.vm.provider "virtualbox" do |v|
    v.name = "zato11"
    v.gui = true
  end

  config.vm.hostname = "zato11"
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  config.vm.define "zato11" do |z|

  # Repository update & install curl
  z.vm.provision "shell", inline: "apt-get update"
  z.vm.provision "shell", inline: "apt-get -y install curl"

  # Helper programs used for installing
  z.vm.provision "shell", inline: "apt-get -y install apt-transport-https"
  z.vm.provision "shell", inline: "apt-get -y install python-software-properties"

  end
end
