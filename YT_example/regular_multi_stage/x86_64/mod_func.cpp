#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;
#if defined(__cplusplus)
extern "C" {
#endif

extern void _BK_gc_reg(void);
extern void _Cabuffer_gc_reg(void);
extern void _CaDynamics_reg(void);
extern void _Ca_HVA_reg(void);
extern void _Ca_LVA_reg(void);
extern void _Cav12_gc_reg(void);
extern void _Cav13_gc_reg(void);
extern void _Cav22_gc_reg(void);
extern void _Cav32_gc_reg(void);
extern void _HCN_gc_reg(void);
extern void _Ih_reg(void);
extern void _Im_reg(void);
extern void _Im_v2_reg(void);
extern void _Kd_reg(void);
extern void _Kir21_gc_reg(void);
extern void _K_P_reg(void);
extern void _K_Pst_reg(void);
extern void _K_T_reg(void);
extern void _K_Tst_reg(void);
extern void _Kv11_gc_reg(void);
extern void _Kv14_gc_reg(void);
extern void _Kv21_gc_reg(void);
extern void _Kv2like_reg(void);
extern void _Kv3_1_reg(void);
extern void _Kv34_gc_reg(void);
extern void _Kv42_gc_reg(void);
extern void _Kv723_gc_reg(void);
extern void _na8st_gc_reg(void);
extern void _Nap_Et2_reg(void);
extern void _Nap_reg(void);
extern void _NaTa_reg(void);
extern void _NaTa_t_reg(void);
extern void _NaTg_reg(void);
extern void _NaTs2_t_reg(void);
extern void _NaTs_reg(void);
extern void _NaV_reg(void);
extern void _SK2_gc_reg(void);
extern void _SK_reg(void);

void modl_reg() {
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");
    fprintf(stderr, " \"mechanisms/BK_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Cabuffer_gc.mod\"");
    fprintf(stderr, " \"mechanisms/CaDynamics.mod\"");
    fprintf(stderr, " \"mechanisms/Ca_HVA.mod\"");
    fprintf(stderr, " \"mechanisms/Ca_LVA.mod\"");
    fprintf(stderr, " \"mechanisms/Cav12_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Cav13_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Cav22_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Cav32_gc.mod\"");
    fprintf(stderr, " \"mechanisms/HCN_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Ih.mod\"");
    fprintf(stderr, " \"mechanisms/Im.mod\"");
    fprintf(stderr, " \"mechanisms/Im_v2.mod\"");
    fprintf(stderr, " \"mechanisms/Kd.mod\"");
    fprintf(stderr, " \"mechanisms/Kir21_gc.mod\"");
    fprintf(stderr, " \"mechanisms/K_P.mod\"");
    fprintf(stderr, " \"mechanisms/K_Pst.mod\"");
    fprintf(stderr, " \"mechanisms/K_T.mod\"");
    fprintf(stderr, " \"mechanisms/K_Tst.mod\"");
    fprintf(stderr, " \"mechanisms/Kv11_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Kv14_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Kv21_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Kv2like.mod\"");
    fprintf(stderr, " \"mechanisms/Kv3_1.mod\"");
    fprintf(stderr, " \"mechanisms/Kv34_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Kv42_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Kv723_gc.mod\"");
    fprintf(stderr, " \"mechanisms/na8st_gc.mod\"");
    fprintf(stderr, " \"mechanisms/Nap_Et2.mod\"");
    fprintf(stderr, " \"mechanisms/Nap.mod\"");
    fprintf(stderr, " \"mechanisms/NaTa.mod\"");
    fprintf(stderr, " \"mechanisms/NaTa_t.mod\"");
    fprintf(stderr, " \"mechanisms/NaTg.mod\"");
    fprintf(stderr, " \"mechanisms/NaTs2_t.mod\"");
    fprintf(stderr, " \"mechanisms/NaTs.mod\"");
    fprintf(stderr, " \"mechanisms/NaV.mod\"");
    fprintf(stderr, " \"mechanisms/SK2_gc.mod\"");
    fprintf(stderr, " \"mechanisms/SK.mod\"");
    fprintf(stderr, "\n");
  }
  _BK_gc_reg();
  _Cabuffer_gc_reg();
  _CaDynamics_reg();
  _Ca_HVA_reg();
  _Ca_LVA_reg();
  _Cav12_gc_reg();
  _Cav13_gc_reg();
  _Cav22_gc_reg();
  _Cav32_gc_reg();
  _HCN_gc_reg();
  _Ih_reg();
  _Im_reg();
  _Im_v2_reg();
  _Kd_reg();
  _Kir21_gc_reg();
  _K_P_reg();
  _K_Pst_reg();
  _K_T_reg();
  _K_Tst_reg();
  _Kv11_gc_reg();
  _Kv14_gc_reg();
  _Kv21_gc_reg();
  _Kv2like_reg();
  _Kv3_1_reg();
  _Kv34_gc_reg();
  _Kv42_gc_reg();
  _Kv723_gc_reg();
  _na8st_gc_reg();
  _Nap_Et2_reg();
  _Nap_reg();
  _NaTa_reg();
  _NaTa_t_reg();
  _NaTg_reg();
  _NaTs2_t_reg();
  _NaTs_reg();
  _NaV_reg();
  _SK2_gc_reg();
  _SK_reg();
}

#if defined(__cplusplus)
}
#endif
