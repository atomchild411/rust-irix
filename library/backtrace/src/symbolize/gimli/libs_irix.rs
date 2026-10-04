// IRIX has no dl_iterate_phdr. Rust code is linked into the executable, and IRIX executables are
// not position independent, so the executable alone, at its link-time addresses, is enough to name
// Rust frames. Frames in shared objects (libc, libpthread) stay unnamed.

use super::mystd::env;
use super::{Library, LibrarySegment};
use alloc::vec::Vec;

unsafe extern "C" {
    /// The ELF header, which the linker loads at the start of the executable's first segment.
    static __ehdr_start: Elf32Ehdr;
}

#[repr(C)]
struct Elf32Ehdr {
    e_ident: [u8; 16],
    e_type: u16,
    e_machine: u16,
    e_version: u32,
    e_entry: u32,
    e_phoff: u32,
    e_shoff: u32,
    e_flags: u32,
    e_ehsize: u16,
    e_phentsize: u16,
    e_phnum: u16,
    e_shentsize: u16,
    e_shnum: u16,
    e_shstrndx: u16,
}

#[repr(C)]
struct Elf32Phdr {
    p_type: u32,
    p_offset: u32,
    p_vaddr: u32,
    p_paddr: u32,
    p_filesz: u32,
    p_memsz: u32,
    p_flags: u32,
    p_align: u32,
}

const PT_LOAD: u32 = 1;

pub(super) fn native_libraries() -> Vec<Library> {
    let Ok(name) = env::current_exe() else {
        return Vec::new();
    };
    let mut segments = Vec::new();
    unsafe {
        let ehdr = &raw const __ehdr_start;
        if (*ehdr).e_ident[..4] != *b"\x7fELF"
            || usize::from((*ehdr).e_phentsize) != size_of::<Elf32Phdr>()
        {
            return Vec::new();
        }
        let phdrs = ehdr.cast::<u8>().add((*ehdr).e_phoff as usize).cast::<Elf32Phdr>();
        for i in 0..usize::from((*ehdr).e_phnum) {
            let ph = &*phdrs.add(i);
            if ph.p_type == PT_LOAD {
                segments.push(LibrarySegment {
                    stated_virtual_memory_address: ph.p_vaddr as usize,
                    len: ph.p_memsz as usize,
                });
            }
        }
    }
    let mut libraries = Vec::new();
    libraries.push(Library { name: name.into_os_string(), segments, bias: 0 });
    libraries
}
