package io.lumenforge.cardfront3d

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.util.Log
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.view.WindowManager
import android.webkit.ConsoleMessage
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import java.io.File
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.StandardCopyOption
import kotlin.math.roundToInt

/**
 * CARDFRONT 3D: Cradle of Echoes — Android Native Kotlin/Jetpack Host (`android_native`).
 *
 * Hosts the hardware-accelerated WebGL2 / Three.js Tactical TCG runtime inside a full-screen
 * sensor-landscape `ComponentActivity` with 120Hz adaptive refresh rate pacing, Android
 * `VibrationEffect` haptics (`createPredefined` + `createWaveform`), and atomic Save Schema v3
 * persistence (`filesDir/save_v3.json`).
 *
 * Enforces 100% Google Play Store compliance with zero cryptocurrency, NFT, or web3 SDKs.
 */
class CardFrontAndroidNativeHost : ComponentActivity() {

    companion object {
        const val TAG: String = "CardFrontAndroidHost"
        const val PACKAGE_ID: String = "io.lumenforge.cardfront3d"
        const val PLAYABLE_ASSET_URL: String =
            "file:///android_asset/WebPlayable/cardfront_cradle_of_echoes_playable.html"
        const val SAVE_FILENAME: String = "save_v3.json"
        const val JS_BRIDGE_NAME: String = "CardFrontAndroidBridge"
        const val TARGET_REFRESH_RATE_HZ: Float = 120.0f
    }

    private var webView: WebView? = null
    private lateinit var androidBridge: CardFrontAndroidBridge

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        configureImmersiveLandscapeAnd120HzWindow()

        androidBridge = CardFrontAndroidBridge(applicationContext)

        val acceleratedWebView = WebView(this).apply {
            setBackgroundColor(Color.parseColor("#080D18"))
            setLayerType(View.LAYER_TYPE_HARDWARE, null)
            isFocusable = true
            isFocusableInTouchMode = true
            keepScreenOn = true

            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                mediaPlaybackRequiresUserGesture = false
                allowFileAccess = true
                allowContentAccess = true
                @Suppress("DEPRECATION")
                allowFileAccessFromFileURLs = true
                @Suppress("DEPRECATION")
                allowUniversalAccessFromFileURLs = true
                cacheMode = WebSettings.LOAD_DEFAULT
                useWideViewPort = true
                loadWithOverviewMode = true
                setSupportZoom(false)
            }

            addJavascriptInterface(androidBridge, JS_BRIDGE_NAME)

            webViewClient = object : WebViewClient() {
                override fun onPageFinished(view: WebView?, url: String?) {
                    super.onPageFinished(view, url)
                    injectNativeHostBootstrap(view)
                }

                override fun shouldOverrideUrlLoading(
                    view: WebView?,
                    request: WebResourceRequest?
                ): Boolean {
                    return false
                }
            }

            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                    consoleMessage?.let {
                        Log.d(
                            TAG,
                            "[WebPlayable:${it.lineNumber()}] ${it.message()}"
                        )
                    }
                    return true
                }
            }
        }

        setContentView(acceleratedWebView)
        acceleratedWebView.loadUrl(PLAYABLE_ASSET_URL)
        webView = acceleratedWebView
    }

    private fun configureImmersiveLandscapeAnd120HzWindow() {
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        val params = window.attributes
        params.preferredRefreshRate = TARGET_REFRESH_RATE_HZ
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            params.layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        }
        window.attributes = params

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            window.setDecorFitsSystemWindows(false)
            window.insetsController?.let { controller ->
                controller.hide(
                    WindowInsets.Type.statusBars() or WindowInsets.Type.navigationBars()
                )
                controller.systemBarsBehavior =
                    WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            }
        } else {
            @Suppress("DEPRECATION")
            window.decorView.systemUiVisibility = (
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    or View.SYSTEM_UI_FLAG_FULLSCREEN
            )
        }
    }

    private fun injectNativeHostBootstrap(targetWebView: WebView?) {
        val bootstrapJs = """
            (function() {
                window.CARDFRONT_NATIVE_HOST = {
                    platform: "android_native",
                    packageId: "$PACKAGE_ID",
                    hardwareAccelerated: true,
                    refreshRateHz: 120,
                    triggerHaptics: function(style, intensity) {
                        if (window.CardFrontAndroidBridge && typeof window.CardFrontAndroidBridge.postHaptic === "function") {
                            return window.CardFrontAndroidBridge.postHaptic(String(style || "medium"), Number(intensity || 0.8));
                        }
                        return false;
                    },
                    syncSaveV3: function(payload) {
                        if (window.CardFrontAndroidBridge && typeof window.CardFrontAndroidBridge.saveEnvelopeV3 === "function") {
                            var serialized = typeof payload === "string" ? payload : JSON.stringify(payload);
                            return window.CardFrontAndroidBridge.saveEnvelopeV3(serialized);
                        }
                        return false;
                    },
                    loadSaveV3: function() {
                        if (window.CardFrontAndroidBridge && typeof window.CardFrontAndroidBridge.loadEnvelopeV3 === "function") {
                            return window.CardFrontAndroidBridge.loadEnvelopeV3();
                        }
                        return "";
                    }
                };
            })();
        """.trimIndent()
        targetWebView?.evaluateJavascript(bootstrapJs, null)
    }

    override fun onResume() {
        super.onResume()
        webView?.onResume()
    }

    override fun onPause() {
        webView?.onPause()
        super.onPause()
    }

    override fun onDestroy() {
        webView?.let { view ->
            view.stopLoading()
            view.removeJavascriptInterface(JS_BRIDGE_NAME)
            view.destroy()
        }
        webView = null
        super.onDestroy()
    }
}

/**
 * JavascriptInterface bridge exposed as `window.CardFrontAndroidBridge` to the WebPlayable runtime.
 *
 * Provides:
 * - `postHaptic(style: String, intensity: Double)` mapping `light`, `medium`, `heavy`, `selection`,
 *   `rigid`, `soft`, `success`, `warning`, `error` to Android `VibrationEffect.createPredefined`
 *   and `VibrationEffect.createWaveform`.
 * - `saveEnvelopeV3(jsonPayload: String)` atomic temp-file + rename persistence to `filesDir/save_v3.json`.
 * - `loadEnvelopeV3(): String` reading the persisted Save Schema v3 JSON envelope.
 */
class CardFrontAndroidBridge(private val context: Context) {

    private val saveLock = Any()

    val saveFile: File
        get() = File(context.filesDir, CardFrontAndroidNativeHost.SAVE_FILENAME)

    @JavascriptInterface
    fun postHaptic(style: String, intensity: Double): Boolean {
        val vibrator = resolveVibrator() ?: return false
        if (!vibrator.hasVibrator()) {
            return false
        }

        val normalizedStyle = style.trim().lowercase()
        val clampedIntensity = intensity.coerceIn(0.05, 1.0)
        val scaledAmplitude = (clampedIntensity * 255.0).roundToInt().coerceIn(1, 255)

        val effect: VibrationEffect = when (normalizedStyle) {
            "light", "soft", "die_nudge" -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK)
                } else {
                    VibrationEffect.createWaveform(
                        longArrayOf(0L, 12L),
                        intArrayOf(0, (scaledAmplitude * 0.65).roundToInt().coerceIn(1, 255)),
                        -1
                    )
                }
            }
            "medium", "card_place" -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK)
                } else {
                    VibrationEffect.createWaveform(
                        longArrayOf(0L, 18L),
                        intArrayOf(0, scaledAmplitude),
                        -1
                    )
                }
            }
            "heavy", "rigid", "card_flip" -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    VibrationEffect.createPredefined(VibrationEffect.EFFECT_HEAVY_CLICK)
                } else {
                    VibrationEffect.createWaveform(
                        longArrayOf(0L, 24L, 28L, 36L),
                        intArrayOf(0, scaledAmplitude, 0, scaledAmplitude),
                        -1
                    )
                }
            }
            "selection" -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK)
                } else {
                    VibrationEffect.createOneShot(10L, scaledAmplitude)
                }
            }
            "success", "victory" -> {
                VibrationEffect.createWaveform(
                    longArrayOf(0L, 24L, 36L, 28L, 36L, 60L),
                    intArrayOf(
                        0,
                        (scaledAmplitude * 0.80).roundToInt().coerceIn(1, 255),
                        0,
                        (scaledAmplitude * 0.90).roundToInt().coerceIn(1, 255),
                        0,
                        scaledAmplitude
                    ),
                    -1
                )
            }
            "warning", "telegraph_alert" -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    VibrationEffect.createPredefined(VibrationEffect.EFFECT_DOUBLE_CLICK)
                } else {
                    VibrationEffect.createWaveform(
                        longArrayOf(0L, 18L, 24L, 22L),
                        intArrayOf(0, scaledAmplitude, 0, scaledAmplitude),
                        -1
                    )
                }
            }
            "error", "defeat" -> {
                VibrationEffect.createWaveform(
                    longArrayOf(0L, 42L, 48L, 68L),
                    intArrayOf(
                        0,
                        scaledAmplitude,
                        0,
                        (scaledAmplitude * 0.95).roundToInt().coerceIn(1, 255)
                    ),
                    -1
                )
            }
            else -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK)
                } else {
                    VibrationEffect.createOneShot(16L, scaledAmplitude)
                }
            }
        }

        return try {
            vibrator.vibrate(effect)
            true
        } catch (ex: Exception) {
            Log.w(CardFrontAndroidNativeHost.TAG, "Failed to dispatch VibrationEffect ($normalizedStyle): ${ex.message}")
            false
        }
    }

    @JavascriptInterface
    fun saveEnvelopeV3(jsonPayload: String): Boolean {
        val trimmed = jsonPayload.trim()
        if (trimmed.isEmpty() || !trimmed.startsWith("{") || !trimmed.endsWith("}")) {
            Log.w(CardFrontAndroidNativeHost.TAG, "Rejected malformed Save Schema v3 JSON payload.")
            return false
        }

        synchronized(saveLock) {
            return try {
                val targetDir = context.filesDir
                if (!targetDir.exists()) {
                    targetDir.mkdirs()
                }

                val targetFile = File(targetDir, CardFrontAndroidNativeHost.SAVE_FILENAME)
                val tempFile = File(targetDir, "${CardFrontAndroidNativeHost.SAVE_FILENAME}.tmp")
                val backupFile = File(targetDir, "${CardFrontAndroidNativeHost.SAVE_FILENAME}.bak")

                tempFile.writeText(trimmed, StandardCharsets.UTF_8)

                if (targetFile.exists()) {
                    Files.move(
                        targetFile.toPath(),
                        backupFile.toPath(),
                        StandardCopyOption.REPLACE_EXISTING
                    )
                }

                try {
                    Files.move(
                        tempFile.toPath(),
                        targetFile.toPath(),
                        StandardCopyOption.ATOMIC_MOVE,
                        StandardCopyOption.REPLACE_EXISTING
                    )
                } catch (_: Exception) {
                    if (!tempFile.renameTo(targetFile)) {
                        Files.move(
                            tempFile.toPath(),
                            targetFile.toPath(),
                            StandardCopyOption.REPLACE_EXISTING
                        )
                    }
                }
                true
            } catch (ex: Exception) {
                Log.e(CardFrontAndroidNativeHost.TAG, "Atomic save_v3.json write failed: ${ex.message}", ex)
                false
            }
        }
    }

    @JavascriptInterface
    fun loadEnvelopeV3(): String {
        synchronized(saveLock) {
            return try {
                val primaryFile = File(context.filesDir, CardFrontAndroidNativeHost.SAVE_FILENAME)
                val backupFile = File(context.filesDir, "${CardFrontAndroidNativeHost.SAVE_FILENAME}.bak")

                when {
                    primaryFile.exists() && primaryFile.length() > 0L -> {
                        primaryFile.readText(StandardCharsets.UTF_8)
                    }
                    backupFile.exists() && backupFile.length() > 0L -> {
                        backupFile.readText(StandardCharsets.UTF_8)
                    }
                    else -> ""
                }
            } catch (ex: Exception) {
                Log.e(CardFrontAndroidNativeHost.TAG, "Failed reading save_v3.json: ${ex.message}", ex)
                ""
            }
        }
    }

    private fun resolveVibrator(): Vibrator? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val manager =
                context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
            manager?.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
        }
    }
}
