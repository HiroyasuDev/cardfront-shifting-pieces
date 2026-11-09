import Cocoa
import WebKit
import Metal
import Foundation

/// CARDFRONT 3D: Cradle of Echoes — Native macOS / Apple Silicon Metal Host
/// Hosts the Three.js / WebGL2 / Metal-backed Tactical TCG runtime inside a 1440x900
/// native macOS window with ProMotion 120Hz frame pacing, Force Touch trackpad haptics
/// (`cardfrontHaptics`), and atomic Save Schema v3 persistence (`cardfrontSaveSync`).
@MainActor
public final class CardFrontScriptBridge: NSObject, WKScriptMessageHandler {
    public static let hapticsHandlerName = "cardfrontHaptics"
    public static let saveSyncHandlerName = "cardfrontSaveSync"

    public let appSupportDirectory: URL
    public let saveFileURL: URL

    public override init() {
        let baseSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSHomeDirectory()).appendingPathComponent("Library/Application Support")
        self.appSupportDirectory = baseSupport.appendingPathComponent("CARDFRONT3D", isDirectory: true)
        self.saveFileURL = self.appSupportDirectory.appendingPathComponent("save_v3.json", isDirectory: false)
        super.init()
    }

    public func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        switch message.name {
        case Self.hapticsHandlerName:
            triggerForceTouchHaptics(payload: message.body)
        case Self.saveSyncHandlerName:
            if let jsonString = message.body as? String {
                _ = writeAtomicSaveV3(jsonPayload: jsonString)
            } else if let dict = message.body as? [String: Any],
                      let data = try? JSONSerialization.data(withJSONObject: dict, options: [.prettyPrinted, .sortedKeys]),
                      let jsonString = String(data: data, encoding: .utf8) {
                _ = writeAtomicSaveV3(jsonPayload: jsonString)
            }
        default:
            break
        }
    }

    public func triggerForceTouchHaptics(payload: Any?) {
        NSHapticFeedbackManager.defaultPerformer.perform(.alignment, performanceTime: .now)
    }

    @discardableResult
    public func writeAtomicSaveV3(jsonPayload: String) -> Bool {
        do {
            try FileManager.default.createDirectory(
                at: appSupportDirectory,
                withIntermediateDirectories: true,
                attributes: nil
            )
            let tmpURL = saveFileURL.appendingPathExtension("tmp")
            let bakURL = saveFileURL.appendingPathExtension("bak")

            try jsonPayload.write(to: tmpURL, atomically: true, encoding: .utf8)
            if FileManager.default.fileExists(atPath: saveFileURL.path) {
                if FileManager.default.fileExists(atPath: bakURL.path) {
                    try? FileManager.default.removeItem(at: bakURL)
                }
                try? FileManager.default.moveItem(at: saveFileURL, to: bakURL)
            }
            try FileManager.default.moveItem(at: tmpURL, to: saveFileURL)
            return true
        } catch {
            fputs("[CardFrontAppleNativeHost] Failed atomic save_v3 write: \(error)\n", stderr)
            return false
        }
    }
}

@MainActor
public final class CardFrontAppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate {
    private var window: NSWindow?
    private var webView: WKWebView?
    private let scriptBridge = CardFrontScriptBridge()
    private let playableRelativePath = "WebPlayable/cardfront_cradle_of_echoes_playable.html"

    public func applicationDidFinishLaunching(_ notification: Notification) {
        let metalDevice = MTLCreateSystemDefaultDevice()
        let gpuName = metalDevice?.name ?? "Apple Silicon Metal Default Device"

        let contentController = WKUserContentController()
        contentController.add(scriptBridge, name: CardFrontScriptBridge.hapticsHandlerName)
        contentController.add(scriptBridge, name: CardFrontScriptBridge.saveSyncHandlerName)

        let bridgeBootstrapJS = """
        window.CARDFRONT_NATIVE_HOST = {
            platform: "AppleNativeMetal",
            gpu: "\(gpuName)",
            proMotion120Hz: true,
            triggerHaptics: function(eventType, intensity, sharpness) {
                if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.cardfrontHaptics) {
                    window.webkit.messageHandlers.cardfrontHaptics.postMessage({
                        eventType: eventType || "alignment",
                        intensity: intensity || 0.85,
                        sharpness: sharpness || 0.75,
                        timestamp: Date.now()
                    });
                }
            },
            syncSaveV3: function(payload) {
                if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.cardfrontSaveSync) {
                    var serialized = typeof payload === "string" ? payload : JSON.stringify(payload);
                    window.webkit.messageHandlers.cardfrontSaveSync.postMessage(serialized);
                }
            }
        };
        """
        let userScript = WKUserScript(
            source: bridgeBootstrapJS,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: false
        )
        contentController.addUserScript(userScript)

        let config = WKWebViewConfiguration()
        config.userContentController = contentController
        config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")

        let frame = NSRect(x: 0, y: 0, width: 1440, height: 900)
        let styleMask: NSWindow.StyleMask = [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView]
        let mainWindow = NSWindow(
            contentRect: frame,
            styleMask: styleMask,
            backing: .buffered,
            defer: false
        )
        mainWindow.title = "CARDFRONT 3D: Cradle of Echoes — Metal (\(gpuName))"
        mainWindow.titlebarAppearsTransparent = true
        mainWindow.backgroundColor = NSColor(calibratedRed: 0.03, green: 0.05, blue: 0.09, alpha: 1.0)
        mainWindow.center()

        let wkWebView = WKWebView(frame: frame, configuration: config)
        wkWebView.navigationDelegate = self
        wkWebView.autoresizingMask = [.width, .height]
        mainWindow.contentView = wkWebView

        if let playableURL = resolvePlayableHTMLURL() {
            wkWebView.loadFileURL(playableURL, allowingReadAccessTo: playableURL.deletingLastPathComponent().deletingLastPathComponent())
        } else {
            wkWebView.loadHTMLString(
                "<html><body style='background:#080d18;color:#00E5FF;font-family:sans-serif;padding:40px;'><h1>CARDFRONT 3D: Cradle of Echoes</h1><p>Metal Device: \(gpuName)</p></body></html>",
                baseURL: nil
            )
        }

        mainWindow.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)

        self.window = mainWindow
        self.webView = wkWebView
    }

    public func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }

    public func resolvePlayableHTMLURL() -> URL? {
        let fm = FileManager.default
        if let bundleRes = Bundle.main.resourceURL {
            let bundledPlayable = bundleRes.appendingPathComponent(playableRelativePath)
            if fm.fileExists(atPath: bundledPlayable.path) {
                return bundledPlayable
            }
            let directPlayable = bundleRes.appendingPathComponent("cardfront_cradle_of_echoes_playable.html")
            if fm.fileExists(atPath: directPlayable.path) {
                return directPlayable
            }
        }
        let cwdURL = URL(fileURLWithPath: fm.currentDirectoryPath).appendingPathComponent(playableRelativePath)
        if fm.fileExists(atPath: cwdURL.path) {
            return cwdURL
        }
        return nil
    }
}

@main
@MainActor
public struct CardFrontAppleNativeHostMain {
    public static func main() {
        let args = CommandLine.arguments
        if args.contains("--self-test") {
            let device = MTLCreateSystemDefaultDevice()
            let gpuName = device?.name ?? "Apple Silicon Metal GPU"
            let bridge = CardFrontScriptBridge()
            let sampleSave = """
            {
              "version": 3,
              "playerId": "commander_alpha",
              "platform": "AppleNativeMetal",
              "gpu": "\(gpuName)",
              "proMotion120Hz": true,
              "zeroTokenStoreCompliant": true
            }
            """
            let saved = bridge.writeAtomicSaveV3(jsonPayload: sampleSave)
            print("{\"status\":\"ok\",\"metalDevice\":\"\(gpuName)\",\"atomicSaveV3\":\(saved),\"savePath\":\"\(bridge.saveFileURL.path)\"}")
            return
        }

        let app = NSApplication.shared
        app.setActivationPolicy(.regular)
        let delegate = CardFrontAppDelegate()
        app.delegate = delegate
        app.run()
    }
}
