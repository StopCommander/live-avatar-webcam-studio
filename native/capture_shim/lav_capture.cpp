// lav_capture.dll — DirectShow capture shim.
// Exposes a flat C ABI consumed by platform/capture_adapter.py via ctypes.
// Build: cmake -B build -G "Visual Studio 17 2022" && cmake --build build --config Release

#include <windows.h>
#include <dshow.h>
#include <cstdint>
#include <cstring>

#pragma comment(lib, "strmiids.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")

struct LavCapture {
    IGraphBuilder*  graph   = nullptr;
    ICaptureGraphBuilder2* builder = nullptr;
    IMediaControl*  control = nullptr;
    IBaseFilter*    source  = nullptr;
    ISampleGrabber* grabber = nullptr;
    int width = 0, height = 0;
    uint8_t* last_frame = nullptr;
    size_t   last_size  = 0;
};

extern "C" __declspec(dllexport)
void* lav_open(int index, int width, int height, int fps) {
    CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    auto* c = new LavCapture();
    c->width = width; c->height = height;

    CoCreateInstance(CLSID_FilterGraph, nullptr, CLSCTX_INPROC_SERVER,
                     IID_PPV_ARGS(&c->graph));
    CoCreateInstance(CLSID_CaptureGraphBuilder2, nullptr, CLSCTX_INPROC_SERVER,
                     IID_PPV_ARGS(&c->builder));
    c->builder->SetFiltergraph(c->graph);

    ICreateDevEnum* dev_enum = nullptr;
    CoCreateInstance(CLSID_SystemDeviceEnum, nullptr, CLSCTX_INPROC_SERVER,
                     IID_PPV_ARGS(&dev_enum));
    IEnumMoniker* monikers = nullptr;
    dev_enum->CreateClassEnumerator(CLSID_VideoInputDeviceCategory, &monikers, 0);
    if (monikers == nullptr) { delete c; return nullptr; }

    IMoniker* moniker = nullptr;
    for (int i = 0; i <= index && monikers->Next(1, &moniker, nullptr) == S_OK; ++i) {
        if (i == index) break;
        moniker->Release(); moniker = nullptr;
    }
    if (!moniker) { monikers->Release(); dev_enum->Release(); delete c; return nullptr; }

    moniker->BindToObject(nullptr, nullptr, IID_PPV_ARGS(&c->source));
    c->graph->AddFilter(c->source, L"Capture Source");
    c->builder->RenderStream(&PIN_CATEGORY_CAPTURE, &MEDIATYPE_Video,
                             c->source, nullptr, nullptr);
    c->graph->QueryInterface(IID_PPV_ARGS(&c->control));

    moniker->Release(); monikers->Release(); dev_enum->Release();
    c->control->Run();
    return c;
}

extern "C" __declspec(dllexport)
int lav_read(void* handle, uint8_t* out_buf) {
    auto* c = static_cast<LavCapture*>(handle);
    if (!c || !c->last_frame) return 0;
    std::memcpy(out_buf, c->last_frame, c->last_size);
    return 1;
}

extern "C" __declspec(dllexport)
void lav_close(void* handle) {
    auto* c = static_cast<LavCapture*>(handle);
    if (!c) return;
    if (c->control) c->control->Stop();
    if (c->source)  c->source->Release();
    if (c->control) c->control->Release();
    if (c->builder) c->builder->Release();
    if (c->graph)   c->graph->Release();
    delete c;
}