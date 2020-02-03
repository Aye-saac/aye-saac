# Setup anaconda environment
echo "Creating virtual environment..."
echo
conda env create -f environment.yml;
eval "$(conda shell.bash hook)"
conda activate Ayebot

# Use the separately shared private key to get the private code
echo
echo "Cloning utils..."

# I don't know if you use ssh or a credential manager to handle this! Trying both
git clone https://github.com/Hangsii/secret_alana_utils.git alana_utils
git clone git@github.com:Hangsii/secret_alana_utils.git alana_utils

# Install dependency packages
echo
echo "Installing supporting packages for utils..."
echo
cd alana_utils && pip install -e .

cd $OLDPWD
echo "All done!"