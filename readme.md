## PROJECT STRUCTURE
```
.
├── main
│   ├── __init__.py
│   ├── core.py
│   ├── extensions.py
│   ├── ftu_helper.py
│   ├── cburn_helper.py
│   ├── rburn_helper.py
│   ├── tools.py
│   └── search.py
├── templates
│   ├── base.html
│   ├── index.html
│   ├── cburn_log.html
│   ├── ftu_log.html
│   ├── rburn_log.html
│   ├── tools.html
│   ├── construction.html
│   ├── input_form.html
│   ├── ip_lookup.html
│   ├── nodata.html
│   └── xxxx.html
├── static
│   ├── css
│   ├── js
│   └── images
├── instance
│   └── database.db
├── rack_data
│   └── database.db
├── config.py
├── app.py
```

## Rack Burn Logs Checking

### HOW THE PROGRAM SCRUTINIZES THE TEST (explaination)

For each system...
1. Get the pass/fail result from Rack Burn Database.
2. If pass, the system will pass through the following `tests`.
3. Each test case will gather system info under its specific category.
4. After info gathering, mosts `test` will use it to compare each other in `the same rack`.
5. The majority with `the same result` will lead to set as `match` under specific category.
6. The minority, `fail`.
7. GPU firmrware and retimer will not be compared to other systems but be hard-coded numbers
    base on the requirement. 


### TESTS ###

> Final Result (Pass/Fail)

> CPU
- Speed & Cores
- Linpack HPL

> DIMM
- Total available size
- Stream Memory Bandwidth Test

> DISK
- Disk Speed Test
- Disk FIO Benchmark 128k

> GPU
- Bandwidth Test
- CUDA Linpack HPL
- Threasholds Row-Remapping
- NV Topology
- GDT
- FDT
- FW & Retimer

> BIOS/IPMI/CPLDs
- MB CPLD1 & CPLD2
- Main SWB CPLD
- NVMe BPN CPLD
- Side SWB CPLDs


## Tools

### SUM tool
> BIOS/BMC/CPLD
- Flash
- Default/Reset
- Delete Backup
> GPU
- Check Info
- Update
> Others
- Delete MEL

### Networking
> Search IP/Password
