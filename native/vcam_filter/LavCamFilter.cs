// LavCamFilter — DirectShow virtual camera source filter (C# via DirectShowLib).
// Registered with regsvr32-style COM registration tooling in tools/register_vcam.ps1.
// Publishes frames written by OBSVirtualCamAdapter over a named pipe.

using System;
using System.IO.Pipes;
using System.Threading;
using DirectShowLib;

namespace LavCamFilter
{
    [ComVisible(true)]
    [Guid("B7D4A2E1-9C3F-4A88-9E22-8F1B0C6D5A44")]
    public class LavCamSource : BaseSourceFilter, IBaseFilter
    {
        private const string PipeName = "lavcam_frames";
        private Thread _worker;
        private volatile bool _running;

        public int SetMediaType(AMMediaType mt) { return 0; }
        public int GetMediaType(int iPosition, AMMediaType pmt) => 0;

        protected override int OnRun(DateTime tStart)
        {
            _running = true;
            _worker = new Thread(PumpFrames) { IsBackground = true };
            _worker.Start();
            return 0;
        }

        protected override int OnStop()
        {
            _running = false;
            _worker?.Join(500);
            return 0;
        }

        private void PumpFrames()
        {
            using var pipe = new NamedPipeServerStream(
                PipeName, PipeDirection.In, 1,
                PipeTransmissionMode.Byte, PipeOptions.None);
            pipe.WaitForConnection();
            var buffer = new byte[1280 * 720 * 3];
            while (_running)
            {
                int read = pipe.Read(buffer, 0, buffer.Length);
                if (read <= 0) break;
                DeliverBuffer(buffer, read);
            }
        }
    }
}