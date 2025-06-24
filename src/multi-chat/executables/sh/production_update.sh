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
rm -rf public/storage
rm -rf storage/app/public/root/custom
rm -rf storage/app/public/root/database
rm -rf storage/app/public/root/bin
rm -rf storage/app/public/root/bot

# Recreate storage symlink
php artisan storage:link

# Install and audit frontend dependencies
npm ci --no-audit --no-progress
npm audit fix --force

# Build frontend
npm run build

# Cache Laravel configuration and routes
php artisan route:cache
php artisan view:cache
php artisan config:cache
php artisan optimize
