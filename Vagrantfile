# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/debian-9.3"
  config.vm.synced_folder ".", "/vagrant"
  config.vm.provision "shell", inline: setup
end

def setup
  <<~HEREDOC

    apt install -y \
      git \
      python3-setuptools \
      python3-yaml \
      ;

  HEREDOC
end
