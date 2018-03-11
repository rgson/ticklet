# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/debian-9.3"
  config.vm.synced_folder ".", "/vagrant"
  config.vm.synced_folder ".", "/home/vagrant/ticklet"
  config.vm.provision "shell", inline: setup
end

def setup
  <<~HEREDOC

    apt install -y \
      devscripts \
      equivs \
      fakeroot \
      git \
      git-buildpackage \
      python3-yaml \
      ;

    mk-build-deps -i -s sudo -t 'apt -y' /vagrant/debian/control

  HEREDOC
end
