# Setup anaconda environment
echo "Creating virtual environment..."
echo
conda create -n Ayesaac python=3.7 -y
eval "$(conda shell.bash hook)"
conda activate Ayesaac

# Use the separately shared private key to get the private code
echo
echo "Cloning utils..."
echo
eval $(ssh-agent)
ssh-add utils_github_key.asc
ssh-keyscan -H github.com >> /etc/ssh/ssh_known_hosts
git clone git@github.com:Hangsii/secret_alana_utils.git utils

# Install dependency packages
echo
echo "Installing supporting packages for utils..."
echo
cd utils && pip install -e .

echo
echo "Installing packages for main level..."
echo

cd $OLDPWD && pip install -r requirements.txt
echo "All done!"