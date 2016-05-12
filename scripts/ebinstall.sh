curl --silent --location https://rpm.nodesource.com/setup_4.x | sh -
yum -y install nodejs-4.2.6
yum -y install npm
node -v
npm -v
echo "running npm install"
npm install --unsafe-perm
echo "DONE"
echo "running bower install"
node_modules/.bin/bower install --allow-root
echo "DONE"
echo "running frontend-build:production"
npm run frontend-build:production
echo "DONE"

