
# ProgramRepair

# Install bugscpp

Please read the [requirements](https://github.com/Moirai7/LLMSupportedProgramRepair/edit/main/BugsCpp_README.rst) of bugscpp first. Make sure you have installed:
- Docker: - Please make sure that the Docker daemon is running in the background.
- Python version >= 3.9

```
git clone https://github.com/Moirai7/LLMSupportedProgramRepair.git
make install
```

## Learning CWE-835

### Simple examples


Using bugscpp to test the result:
```
python bugscpp/bugscpp.py checkout juliet 1 --buggy
python bugscpp/bugscpp.py build juliet/buggy-1
python bugscpp/bugscpp.py test juliet/buggy-1 
```
##### task1: guide LLMs to find the vunlerbility

Please guide LLMs to find the vunlerbility. Do not directly tell LLMs how to repair the code. Try to find the minimal knowledge you need to provide.
Starting from introducing the vulnerbility, then giving a large scope of possible incorrect lines, and gradually narrowing down the scope.
Here are the test code:
```
https://samate.nist.gov/SARD/test-cases/122763/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122762/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122761/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122764/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122765/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122766/versions/1.0.0
```
##### task2: Interactively repair the program
1. Ask LLMs to repair the program.
2. Copy the reponse from LLMs to corresponding file
```
vim $your_bugscpp_path$/juliet/buggy-1/testcases/filename.c
```
3. Recompile the project and test the patch
```
python bugscpp/bugscpp.py build juliet/buggy-1
python bugscpp/bugscpp.py test juliet/buggy-1 
```
4. Check whether the generated patch has passed the test case
5. If not, open the output file, and send the error message to LLMs, and repeat from step 1
```
# outpt file is located in
$your_bugscpp_path$/juliet-buggy-1-*/*.output
```
   
### Real world case study -- exiv2

#### Test the case study and analyze the vulnerable code

The correct patch could be found [here](https://github.com/Suresoft-GLaDOS/bugscpp/blob/main/bugscpp/taxonomy/exiv2/patch/0001-buggy.patch).
Run bellowing commands, try to figure out why this has CWE-835 vunlnerbility.

```
python bugscpp/bugscpp.py checkout exiv2 1 --buggy
python bugscpp/bugscpp.py build exiv2/buggy-1
python bugscpp/bugscpp.py test exiv2/buggy-1 
```

#### LLMs supported Program Repiar

##### task1: guide LLMs to find the vunlerbility

Bellowing is the initial prompt. Please guide LLMs to find the vunlerbility. Do not directly tell LLMs how to repair the code. Try to find the minimal knowledge you need to provide.
Starting from introducing the vulnerbility, then giving a large scope of possible incorrect lines, and gradually narrowing down the scope.

```
We are testing Exiv2. The following code has a CWE-835 Vunlerbility

    void JpegBase::printStructure(std::ostream& out, PrintStructureOption option, int depth)
    {
        if (io_->open() != 0)
            throw Error(kerDataSourceOpenFailed, io_->path(), strError());
        // Ensure that this is the correct image type
        if (!isThisType(*io_, false)) {
            if (io_->error() || io_->eof())
                throw Error(kerFailedToReadImageData);
            throw Error(kerNotAJpeg);
        }

        bool bPrint = option == kpsBasic || option == kpsRecursive;
        std::vector<uint32_t> iptcDataSegs;

        if (bPrint || option == kpsXMP || option == kpsIccProfile || option == kpsIptcErase) {
            // nmonic for markers
            std::string nm[256];
            nm[0xd8] = "SOI";
            nm[0xd9] = "EOI";
            nm[0xda] = "SOS";
            nm[0xdb] = "DQT";
            nm[0xdd] = "DRI";
            nm[0xfe] = "COM";

            // 0xe0 .. 0xef are APPn
            // 0xc0 .. 0xcf are SOFn (except 4)
            nm[0xc4] = "DHT";
            for (int i = 0; i <= 15; i++) {
                char MN[16];
                snprintf(MN, sizeof(MN), "APP%d", i);
                nm[0xe0 + i] = MN;
                if (i != 4) {
                    snprintf(MN, sizeof(MN), "SOF%d", i);
                    nm[0xc0 + i] = MN;
                }
            }

            // which markers have a length field?
            bool mHasLength[256];
            for (int i = 0; i < 256; i++)
                mHasLength[i] = (i >= sof0_ && i <= sof15_) || (i >= app0_ && i <= (app0_ | 0x0F)) ||
                                (i == dht_ || i == dqt_ || i == dri_ || i == com_ || i == sos_);

            // Container for the signature
            bool bExtXMP = false;
            long bufRead = 0;
            const long bufMinSize = 36;
            DataBuf buf(bufMinSize);

            // Read section marker
            int marker = advanceToMarker();
            if (marker < 0)
                throw Error(kerNotAJpeg);

            bool done = false;
            bool first = true;
            while (!done) {
                // print marker bytes
                if (first && bPrint) {
                    out << "STRUCTURE OF JPEG FILE: " << io_->path() << std::endl;
                    out << " address | marker       |  length | data" << std::endl;
                    REPORT_MARKER;
                }
                first = false;
                bool bLF = bPrint;

                // Read size and signature
                std::memset(buf.pData_, 0x0, buf.size_);
                bufRead = io_->read(buf.pData_, bufMinSize);
                if (io_->error() || bufRead != bufMinSize)
                    throw Error(kerFailedToReadImageData);
                const uint16_t size = mHasLength[marker] ? getUShort(buf.pData_, bigEndian) : 0;
                if (bPrint && mHasLength[marker])
                    out << Internal::stringFormat(" | %7d ", size);

                // print signature for APPn
                if (marker >= app0_ && marker <= (app0_ | 0x0F)) {
                  ...
                }

                // print COM marker
                if (bPrint && marker == com_) {
                    // size includes 2 for the two bytes for size!
                    const int n = (size - 2) > 32 ? 32 : size - 2;
                    // start after the two bytes
                    out << "| "
                        << Internal::binaryToString(
                               makeSlice(buf, 2, n + 2 /* cannot overflow as n is at most size - 2 */));
                }

                // Skip the segment if the size is known
                if (io_->seek(size - bufRead, BasicIo::cur))
                    throw Error(kerFailedToReadImageData);

                if (bLF)
                    out << std::endl;

                if (marker != sos_) {
                    // Read the beginning of the next segment
                    marker = advanceToMarker();
                    enforce(marker>=0, kerNoImageInInputData);
                    REPORT_MARKER;
                }
                done |= marker == eoi_ || marker == sos_;
                if (done && bPrint)
                    out << std::endl;
            }
        }
        ...
    }  // JpegBase::printStructure
```

##### task2: Interactively repair the program
1. Ask LLMs to repair the program.
2. Copy the reponse from LLMs to corresponding file
```
vim $your_bugscpp_path$/exiv2/buggy-1/src/jpgimage.cpp
```
3. Recompile the project and test the patch
```
python bugscpp/bugscpp.py build exiv2/buggy-1
python bugscpp/bugscpp.py test exiv2/buggy-1 
```
4. Check whether the generated patch has passed the test case
5. If not, open the output file, and send the error message to LLMs, and repeat from step 1
```
# outpt file is located in
$your_bugscpp_path$/exiv2-buggy-1-*/*.output
```
   
