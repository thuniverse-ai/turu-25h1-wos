#!/bin/bash
set -e  # Exit immediately on error

cd ../..

# Install PHP dependencies
composer install --no-dev --optimize-autoloader --no-interaction

# Laravel setup
php artisan key:generate
php artisan migrate --force
php artisan db:seed --class=InitSeeder --force

# Clean up old storage links and directories
rm -f public/storage
rm -f storage/app/public/root/custom
rm -f storage/app/public/root/database
rm -f storage/app/public/root/bin
rm -f storage/app/public/root/bot
rm -f storage/app/public/root/bootstrap/bot

# Recreate storage symlink
php artisan config:cache
php artisan storage:link

# Install and audit frontend dependencies
npm ci --no-audit --no-progress
npm audit fix --force

# Build frontend
npm run build

# Cache Laravel configuration and routes
php artisan route:cache
php artisan view:cache
php artisan optimize
