cd ../..

:: Install PHP dependencies
call composer install --no-dev --optimize-autoloader --no-interaction --ansi

:: Generate app key
call php artisan key:generate --ansi

:: Run DB migration first, then seeder
call php artisan migrate --force --ansi
call php artisan db:seed --class=InitSeeder --force --ansi

:: Clean up old storage links and files
rmdir /Q /S public\storage
rmdir /Q /S storage\app\public\root\custom
rmdir /Q /S storage\app\public\root\database
rmdir /Q /S storage\app\public\root\bin
rmdir /Q /S storage\app\public\root\bot
rmdir /Q /S storage\app\public\root\bootstrap\bot

:: Create new storage link
call php artisan storage:link --ansi

:: Install and audit JS dependencies
call npm ci --no-audit --no-progress --color=always
call npm audit fix --loglevel verbose --force

:: Build frontend assets
call npm run build --color=always

:: Cache and optimize Laravel
call php artisan route:cache --ansi
call php artisan view:cache --ansi
call php artisan config:cache --ansi
call php artisan optimize --ansi
