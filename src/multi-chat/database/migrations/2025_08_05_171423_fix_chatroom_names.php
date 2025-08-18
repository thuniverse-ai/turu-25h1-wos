<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        DB::table('chatrooms')->select('id', 'name')->orderBy('id')->chunk(100, function ($chatrooms) {
            foreach ($chatrooms as $chatroom) {
                $decoded = rawurldecode($chatroom->name);

                $cleanName = iconv('UTF-8', 'UTF-8//IGNORE', $decoded);

                $cleanName = mb_convert_encoding($cleanName, 'UTF-8', 'UTF-8');

                DB::table('chatrooms')
                    ->where('id', $chatroom->id)
                    ->update(['name' => $cleanName]);
            }
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        // This data transformation is irreversible.
    }
};
