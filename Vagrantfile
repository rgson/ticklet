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
    echo 'LC_ALL=en_US.UTF-8' >>/etc/default/locale
    cd /home/vagrant
    apt install -y devscripts fakeroot equivs
    mk-build-deps -i -t 'apt -y' ticklet/debian/control
  HEREDOC
end
