<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Contracts\Queue\ShouldBeUniqueUntilProcessing;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Bus\Queueable;
use App\Models\SystemSetting;
use App\Jobs\RequestChat;
use App\Models\LLMs;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;

class HealthCheck implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * Execute the job.
     *
     * @return void
     */
    public function handle()
    {
        ignore_user_abort(true);
        set_time_limit(0);
        $systemSetting = SystemSetting::where('key', 'kernel_location')->first();

        if ($systemSetting && $systemSetting->value) {
            // Send GET request to the endpoint
            $response = Http::get($systemSetting->value . '/' . RequestChat::$kernel_api_version . '/worker/debug');

            if ($response->ok()) {
                // Get the response body and all LLMs
                $responseData = $response->body();
                $llms = LLMs::select('id', 'access_code')->get();

                // Separate found and not found LLMs
                $foundIds = [];
                foreach ($llms as $llm) {
                    if (strpos($responseData, "'{$llm->access_code}'") !== false || strpos($responseData, "\"{$llm->access_code}\"") !== false) {
                        $foundIds[] = $llm->id;
                    }
                }
                LLMs::whereIn('id', $foundIds)->update([
                    'healthy' => Carbon::now(),
                ]);
            } else {
                Log::error('GET request failed:', ['status' => $response->status()]);
            }
        } else {
            Log::error('No valid endpoint found for kernel_location');
        }
    }
}
