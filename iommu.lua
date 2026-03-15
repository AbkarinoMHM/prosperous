local pcie_cfg_base = Uint64:new(0xF0000000)

function pci_cfg_addr(b, d, f)
    return pcie_cfg_base + b * 0x100000 + d * 0x8000 + f * 0x1000
end

local b0d0f0 = pci_cfg_addr(0, 0, 0)

function smn_read32(addr)
    pw32(b0d0f0 + 0xa0, addr)
    return pr32(b0d0f0 + 0xa4)
end

function smn_write32(addr, val)
    pw32(b0d0f0 + 0xa0, addr)
    pw32(b0d0f0 + 0xa4, val)
end

function smn_read64(addr)
    return Uint64:new(smn_read32(addr).lo, smn_read32(addr + 4).lo)
end

function smn_write64(addr, val)
    val = force_Uint64(val)
    smn_write32(addr, val.lo)
    smn_write32(addr + 4, val.hi)
end

local iommu_addr = 0x2400000
function set_exclusion(base, size)
    -- [51:12] base, [1] allow, [0] enable
    smn_write64(iommu_addr + 0x20, base)
    -- [51:12] limit
    smn_write64(iommu_addr + 0x28, base + size - 1)
    smn_write64(iommu_addr + 0x20, base + 3)
end

function get_exclusion()
    return {
        base = smn_read64(iommu_addr + 0x20),
        limit = smn_read64(iommu_addr + 0x28),
    }
end

local exclusion = get_exclusion()
if exclusion.base.lo ~= 3 or exclusion.limit ~= Uint64:new(0xfffff000, 0xfffff) then
    log('setting exclusion')
    set_exclusion(0, Uint64:new(0xffffffff, 0xffffffff))
    exclusion = get_exclusion()
end
if exclusion.base.lo ~= 3 then
    log('set exclusion failed '..tostring(exclusion.base)..' '..tostring(exclusion.limit))
end

for i=0,0x30,8 do
    local addr = iommu_addr + i
    log(string.format('%8x ', addr)..tostring(smn_read64(addr)))
end
