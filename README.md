
# ProgramRepair


# Install bugscpp

## option 1: If your computer support AMD
Please read the [requirements](https://github.com/Moirai7/LLMSupportedProgramRepair/blob/main/BugsCpp_README.rst) of bugscpp first. 
Make sure you have installed:
- Docker: - Please make sure that the Docker daemon is running in the background.
- Python version >= 3.9

```
git clone https://github.com/Moirai7/LLMSupportedProgramRepair.git
cd LLMSupportedProgramRepair & make install
```
## option 2: If your computer does not support AMD 

For easy setup, if your computer supports virtualbox, you may use vagrant to install an ubuntu VM.
After installing vagrant(https://developer.hashicorp.com/vagrant/downloads) and virtualbox(https://www.virtualbox.org/), the following steps are required:
```
git clone https://github.com/Moirai7/LLMSupportedProgramRepair.git
vagrant up
vagrant ssh #(password: vagrant)
```
Every time when you run `vagrant up`, you have opened the vm(check out your vituralbox desktop).
And when you run `vagrant ssh`, you have logged to the vm. 
Next, you could clone this repo, and run `make install`,

When you run the following experiments("python3.9 bugscpp.py ..."), make sure you have run `vagrant up & vagrant ssh`. And make sure you are modifying files in the VM instead of your local files.

## option3: 
If you are using mac M1, M2, and M3 (still cannot work😭):
1. Download [VMware Fusion 12 Player][https://services.tctc.edu/TDClient/323/InfoTech/KB/ArticleDet?ID=21304] for macOS
2. Use license key from your myVMware account and install the application
3. Allow VMware Fusion to control system events within the app when prompted
4. Enable the accessibility preference at System Preferences > Security & Privacy > Accessibility > VMware Fusion
5. Install [vagrant][https://www.vagrantup.com/downloads]: `brew tap hashicorp/tap && brew install vagrant`
7. Install the [vagrant-vmware-desktop plugin][5]: `vagrant plugin install vagrant-vmware-desktop` (if you got error: `export VAGRANT_DISABLE_STRICT_DEPENDENCY_ENFORCEMENT=1`)
9. Install the [VMware utility][6] for vagrant: `brew install --cask vagrant-vmware-utility`
10. Navigate to the folder containing the Vagrantfile and run `vagrant up --provider=vmware_desktop`. The command might fail on the first run, so try running the same command again.
11. Run `vagrant ssh` to login to the vagrant box. Profit! 

## Notes:
1. Please save the interatcion between you and Chatgpt.
2. For each bugs, your report should answer the following questions:
- Content Understanding: Explain what CWE-xxx is using in this code
- Content Understanding: Explain the output and why these test cases are failed before you repair the code.
- Content Understanding: Explain the output of ChatGPT. Is it correct? Does ChatGPT understand the logic of the code?
- Content Understanding: Attach the interactive conversation. Can ChatGPT repair the code? If the patch is not correct, why? What kind of information is required to repair the code?
- Feedback: Considering the relation between task3(identify vulnerability) and task4(repair program), after locating the vulnerable code, does this help to improve the performance of repairing the program?
- Completion Rates: Did you successfully guide ChatGPT to repair the program?
- Student Reflections: What have you learned in this Lab?

## Learning CWE-835

### Simple examples


#### task1: Read the code and understand what CWE-835 is

Here are the test code:
```
https://samate.nist.gov/SARD/test-cases/122763/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122762/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122761/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122764/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122765/versions/1.0.0
https://samate.nist.gov/SARD/test-cases/122766/versions/1.0.0
```

#### task2: Test the code using bugscpp
First, go to your local directory of this repo
```
cd your_path/
```
Using bugscpp to dowload the code:
```
python bugscpp/bugscpp.py checkout juliet 1 --buggy
```

After downloading, there are a new directory named `juliet`. In the directory, `.repo` is the github repo of the project; `buggy-1` is the first vunlnerbility you will test.

Using bugscpp to build and test the bug:
```
python bugscpp/bugscpp.py build juliet/buggy-1
python bugscpp/bugscpp.py test juliet/buggy-1 
```

The name of test file is listed in `$your_bugscpp_path/taxonomy/juliet/extra/0001/.dpp/test_list`

You may use `-c NUM` to specify a test code, for example,
```
python bugscpp/bugscpp.py test juliet/buggy-1 -c 1
```

The testing result is listed in `$your_bugscpp_path/juliet-buggy-1-1`

In the testing result directory, `NUM.output` is the output of the source code; and `NUM.test` is the test result of the source code.

The test file is under `juliet/buggy-1/testcases/CWE835`. In each test file, there is a bad code and a good code. Your goal is to modify the bad code, so it can pass the test.




#### task3: guide LLMs to find the vulnerability


Please guide LLMs to find the vunlerbility. Do not directly tell LLMs how to repair the code. 

Replace the function name and remove comments in the original code. Try to find the minimal knowledge you need to provide.

If LLMs cannot find the vunlerbility, starting from introducing the vulnerbility, then giving a large scope of possible incorrect lines, and gradually narrowing down the scope.

Example initial prompt:
```
Explain why the code is not correct:
void codeexample() 
{
    int i = 0;
    
    do
    {
        printIntLine(i);
        i = (i + 1) % 256;
    } while(i >= 0);
}
```

#### task4: Interactively repair the program
1. Ask LLMs to repair the program.
2. Copy the response from LLMs to corresponding file. **DO NOT MODIFY THE ORIGINAL FUNCTION NAME** Copy the code body to the corresponding file
```
vim $your_bugscpp_path$/juliet/buggy-1/testcases/filename.c
```
3. Recompile the project and test the patch
```
python bugscpp/bugscpp.py build juliet/buggy-1
python bugscpp/bugscpp.py test juliet/buggy-1 -c NUM
```
4. Check whether the generated patch has passed the test case
5. If not, open the output file, and send the error message to LLMs, and repeat from step 1
```
# outpt file is located in
$your_bugscpp_path$/juliet-buggy-1-*/*.output
```
   
### Real world case study -- exiv2

#### task1: Test the case study and analyze the vulnerable code

The correct patch could be found `bugscpp/taxonomy/exiv2/patch/0001-buggy.patch`.
Run bellowing commands, try to figure out why this has CWE-835 vunlnerbility.

```
python bugscpp/bugscpp.py checkout exiv2 1 --buggy
python bugscpp/bugscpp.py build exiv2/buggy-1
python bugscpp/bugscpp.py test exiv2/buggy-1 
```

Similar as the previous lab, you will find a `exiv2` directory. And `.repo` is the github repo of the project; `buggy-1` is the buggy project. 

The name of test cases is still in `.dpp`. And you can find the test code in `buggy-1/tests/`. Real world project is more complex than the juliet dataset. The test code is not the source code that contains vunlerbilites. These are inputs that will trigger the vunlerbilites in the real world project.

Details of the vunlerbilites are in `bugscpp/taxonomy/exiv2/patch/NUM-buggy.patch`. It lists which file has the vunlerbility and how to modify the file.

In this example, `src/jpgimage.cpp` has issue. So you could go to `exiv2/buggy-1/src/jpgimage.cpp` to find the bug. Your goal is to guild LLMs to locate the vunlerbility in this file and repair this file.


#### task2: guide LLMs to find the vulnerability


Bellowing is the initial prompt. 

Please guide LLMs to find the vunlerbility. 

Do not directly tell LLMs how to repair the code. Try to find the minimal knowledge you need to provide.

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

#### task3: Interactively repair the program
1. Ask LLMs to repair the program.
2. Copy the response from LLMs to corresponding file
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

## Learning CWE-190
Please review the code here to understand what is CWE-190:
https://samate.nist.gov/SARD/test-cases/235788/versions/2.0.0

### Real world case study - exiv2

Please follow the three tasks in previous section: test the code, locate the vunlnerbility, and repair the program. 

The buggy id for this CWE is 4. So you could run the following command to test the bug.
```
python bugscpp/bugscpp.py checkout exiv2 4 --buggy
python bugscpp/bugscpp.py build exiv2/buggy-4
python bugscpp/bugscpp.py test exiv2/buggy-4
```

Details of the vunlerbilites are in `bugscpp/taxonomy/exiv2/patch/0004-buggy.patch`. And you can find the source code filename in the patch file, which is src/nikonmn_int.cpp. So you need to find the file and the corresponding incorrect function. 

You goal is to guild GPT to find the incorrect lines and repair the program.


## Learning CWE-125
Please review the code here to understand what is CWE-125:
https://cwe.mitre.org/data/definitions/125.html


### Real world case study - exiv2

Please follow the three tasks in previous section: test the code, locate the vunlnerbility, and repair the program. 

The buggy id for this CWE is 6. So you could run the following command to test the bug.
```
python bugscpp/bugscpp.py checkout exiv2 6 --buggy
python bugscpp/bugscpp.py build exiv2/buggy-6
python bugscpp/bugscpp.py test exiv2/buggy-6
```

Details of the vunlerbilites are in `bugscpp/taxonomy/exiv2/patch/0006-buggy.patch`. And you can find the source code filename in the patch file. So you need to find the file and the corresponding incorrect function. 

You goal is to guild GPT to find the incorrect lines and repair the program.



