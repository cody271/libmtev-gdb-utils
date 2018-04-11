# Copyright (c) 2018, Circonus, Inc. and contributors.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
#  * Neither the name of Circonus, Inc. nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import gdb

#
# ck_hs_t* keys -> (entries)
#
def ck_hs_keys(ck_hs):
    ck_hs_map = ck_hs["map"]
    entries = ck_hs_map["entries"]
    capacity = int(ck_hs_map["capacity"])
    n_entries = int(ck_hs_map["n_entries"])
    res = []
    for i in range(capacity):
        entry = int(entries[i])
        if entry != 0:
            res.append(entry)
    assert len(res) == n_entries
    return tuple(res)

#
# dereference lua_State**
#
def Lptr(L):
    Lptr_expr = "((lua_State **)0x%x)[0]" % L
    return gdb.parse_and_eval(Lptr_expr)

#
# ck_hs_t* entry -> ck_hash_attr_t* (mtev_hash.h)
#
_CK_CC_CONTAINER_expr = "(ck_hash_attr_t *)(void *)(((char *)0x%x) - ((size_t)&((ck_hash_attr_t *)0)->key))"
def index_attribute_container(entry):
    entry_expr = _CK_CC_CONTAINER_expr % entry
    return gdb.parse_and_eval(entry_expr)

#
# ck_hs_t* entry -> lua_State*
#
def ck_hs_entry_to_L(entry):
    mtev_entry = index_attribute_container(entry)
    key_ptr = mtev_entry["key_ptr"]
    return Lptr(key_ptr)

#
# mtev_hash_table* -> ck_hs_t*
#
def mtev_to_ck_hs(mtev_ht):
    return mtev_ht["u"]["hs"]

#
# "symbol" (mtev_hash_table*) -> (L)
#
def mtev_L(sym_mtev_ht):
    mtev_ht, _ = gdb.lookup_symbol(sym_mtev_ht)
    assert mtev_ht, "Failed to load symbol: %s" % sym_mtev_ht
    ck_hs = mtev_to_ck_hs(mtev_ht.value())
    ck_keys = ck_hs_keys(ck_hs)
    return tuple(map(ck_hs_entry_to_L, ck_keys))

