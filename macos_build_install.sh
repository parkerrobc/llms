pyInstaller llms.spec

if [ -d "/usr/local/bin" ]; then
  echo "/usr/local/bin already exists"
  rm -rf /usr/local/bin/llms
  echo "/usr/local/bin/llms removed"
else
  sudo mkdir -p -m 775 /usr/local/bin
fi

if [ ! -f "~/.bash_profile" ]; then
  echo $"you may need to add\nexport PATH=$PATH:/usr/local/bin\nto your .bash_profile"
else
  touch ~/.bash_profile
  echo 'export PATH=$PATH:/usr/local/bin' > ~/.bash_profile
  echo "created ~/.bash_profile"
fi

if [ ! -f "~/.zshrc" ]; then
  echo $"you may need to add\nexport PATH=$PATH:/usr/local/bin\nto your .zshrc"
else
  touch ~/.zshrc
  echo 'export PATH=$PATH:/usr/local/bin' > ~/.zshrc
  echo "created ~/.zshrc"
fi

echo "installing latest llms"
sudo cp dist/llms /usr/local/bin
echo "installation complete"
