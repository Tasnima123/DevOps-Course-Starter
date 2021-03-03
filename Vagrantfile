Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/bionic64"
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
  sudo apt-get update
  sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
  xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

  git clone https://github.com/pyenv/pyenv.git /home/vagrant/.pyenv
  chown vagrant:vagrant .pyenv
  echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> /home/vagrant/.bashrc
  echo 'eval "$(pyenv init -)"' >> /home/vagrant/.bashrc

  export PATH="$HOME/.pyenv/bin:$PATH"
  export PATH="/home/vagrant/.pyenv/shims:$PATH"
  pyenv rehash

  pyenv install 3.8.5
  pyenv global 3.8.5

  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

  source $HOME/.poetry/env
  
  SHELL
end