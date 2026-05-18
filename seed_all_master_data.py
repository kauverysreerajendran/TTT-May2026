"""
CONSOLIDATED MASTER DATA SEED SCRIPT
TTT Enterprise Manufacturing Workflow System

Loads ALL master data in one run. Safe to re-run (idempotent).

Usage:
    env\\Scripts\\python.exe seed_all_master_data.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction

print("=" * 60)
print("TTT MASTER DATA SEED — STARTING")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# 1. ADMIN USER
# ─────────────────────────────────────────────────────────────
print("\n[1/14] Admin User ...")
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@ttt.local', 'admin')
    print("  ✅ Created  admin / admin")
else:
    u = User.objects.get(username='admin')
    u.set_password('admin')
    u.save()
    print("  ℹ️  Exists  — password reset to 'admin'")
ADMIN = u

# ─────────────────────────────────────────────────────────────
# 2. TRAY TYPES
# ─────────────────────────────────────────────────────────────
print("\n[2/14] Tray Types ...")
from modelmasterapp.models import TrayType

TRAY_TYPES = [
    ('Normal', 16),
    ('Jumbo',  12),
]
for name, cap in TRAY_TYPES:
    obj, created = TrayType.objects.get_or_create(
        tray_type=name, defaults={'tray_capacity': cap, 'createdby': ADMIN}
    )
    print(f"  {'✅ Created' if created else 'ℹ️  Exists '} {name} (cap={obj.tray_capacity})")

normal_tray = TrayType.objects.get(tray_type='Normal')
jumbo_tray  = TrayType.objects.get(tray_type='Jumbo')

# ─────────────────────────────────────────────────────────────
# 3. POLISH FINISH TYPES
# ─────────────────────────────────────────────────────────────
print("\n[3/14] Polish Finish Types ...")
from modelmasterapp.models import PolishFinishType

POLISH_TYPES = [
    ('Shotblasting (S)', 'S'),
    ('Buffed (A)',       'A'),
    ('Bi-Finish (B)',   'B'),
    ('Bi-Finish (C)',   'C'),
]
for name, internal in POLISH_TYPES:
    obj, created = PolishFinishType.objects.get_or_create(
        polish_internal=internal,
        defaults={'polish_finish': name, 'createdby': ADMIN}
    )
    print(f"  {'✅ Created' if created else 'ℹ️  Exists '} {name}")

shotblasting = PolishFinishType.objects.get(polish_internal='S')
buffed       = PolishFinishType.objects.get(polish_internal='A')
bi_finish    = PolishFinishType.objects.get(polish_internal='B')
chrome_finish= PolishFinishType.objects.get(polish_internal='C')

# ─────────────────────────────────────────────────────────────
# 4. CATEGORIES
# ─────────────────────────────────────────────────────────────
print("\n[4/14] Categories ...")
from modelmasterapp.models import Category

CATEGORIES = ['New Product', 'Regular', 'Align']
for name in CATEGORIES:
    obj, created = Category.objects.get_or_create(
        category_name=name, defaults={'createdby': ADMIN}
    )
    print(f"  {'✅ Created' if created else 'ℹ️  Exists '} {name}")

# ─────────────────────────────────────────────────────────────
# 5. VENDORS
# ─────────────────────────────────────────────────────────────
print("\n[5/14] Vendors ...")
from modelmasterapp.models import Vendor

VENDORS = [
    ('Demo Vendor',  'Demo'),
    ('Demo2 Vendor', 'Demo2'),
]
for vname, vinternal in VENDORS:
    obj, created = Vendor.objects.get_or_create(
        vendor_internal=vinternal,
        defaults={'vendor_name': vname, 'createdby': ADMIN}
    )
    print(f"  {'✅ Created' if created else 'ℹ️  Exists '} {vname}")

demo_vendor  = Vendor.objects.get(vendor_internal='Demo')
demo2_vendor = Vendor.objects.get(vendor_internal='Demo2')

# ─────────────────────────────────────────────────────────────
# 6. VERSIONS
# ─────────────────────────────────────────────────────────────
print("\n[6/14] Versions ...")
from modelmasterapp.models import Version

VERSIONS = ['A', 'B', 'C', 'D', 'E', 'F', 'K', 'L', 'P', 'R']
for v in VERSIONS:
    obj, created = Version.objects.get_or_create(
        version_internal=v,
        defaults={'version_name': v, 'createdby': ADMIN}
    )
    print(f"  {'✅ Created' if created else 'ℹ️  Exists '} Version {v}")

# helpers
def get_ver(internal):
    return Version.objects.get(version_internal=internal)

# ─────────────────────────────────────────────────────────────
# 7. PLATING COLORS  (client data — 27 colors with zone routing)
# ─────────────────────────────────────────────────────────────
print("\n[7/14] Plating Colors ...")
from modelmasterapp.models import Plating_Color

# (display_name, internal_code, zone1_IPS_only, zone2)
PLATING_COLORS = [
    ('BLACK',           'N',    False, True),
    ('IPS',             'S',    True,  False),   # Zone 1 only
    ('IPG',             'Y',    False, True),
    ('IP-GUN',          'GUN',  False, True),
    ('IP-BROWN',        'BRN',  False, True),
    ('RG',              'W',    False, True),
    ('IPSIPG',          'B',    False, True),
    ('IP-BLUE M',       'BLU',  False, True),
    ('RG-BI',           'RGSS', False, True),
    ('IPG-2N',          '2N',   False, True),
    ('IPSIPG-HN',       'HN',   False, True),
    ('IP-CORN.GOLD',    'CN',   False, True),
    ('IP-TITANIUM',     'T',    False, True),
    ('IPG-HALF.N',      'YHN',  False, True),
    ('ANODISING',       'A',    False, True),
    ('IP-BLUE INH',     'BL01', False, True),
    ('IP-BLUE',         'BLU2', False, True),
    ('IP-BR ANTI',      'BA',   False, True),
    ('IP-BRONZE',       'BRZ',  False, True),
    ('IP-CH.GOLD',      'CHG',  False, True),
    ('IP-SIL ANTI',     'SA',   False, True),
    ('IP-LCR',          'LCR',  False, True),
    ('IP-OGR',          'OGR',  False, True),
    ('IP-ICE BLUE',     'IBL',  False, True),
    ('IP-PLUM',         'PM01', False, True),
    ('IP-TITANIUM BLUE','TIN',  False, True),
    ('IPSIPG-2N',       'B2N',  False, True),
]

# Clear and reload to get clean state
Plating_Color.objects.all().delete()
for name, internal, z1, z2 in PLATING_COLORS:
    Plating_Color.objects.create(
        plating_color=name,
        plating_color_internal=internal,
        jig_unload_zone_1=z1,
        jig_unload_zone_2=z2,
        createdby=ADMIN,
    )
    zone = "Zone 1" if z1 else "Zone 2"
    print(f"  ✅ {name} ({internal}) → {zone}")
print(f"  Total: {Plating_Color.objects.count()} colors")

# ─────────────────────────────────────────────────────────────
# 8. TRAY IDs (500 per prefix: NB, JB, NR, JR, NL, JL, ND, JD)
# ─────────────────────────────────────────────────────────────
print("\n[8/14] Tray IDs ...")
from modelmasterapp.models import TrayId

PREFIXES = ['NR', 'JR', 'ND', 'JD', 'NL', 'JL', 'NB', 'JB']
PER_PREFIX = 500
total_created = 0

with transaction.atomic():
    for prefix in PREFIXES:
        is_normal = prefix.startswith('N')
        tt = normal_tray if is_normal else jumbo_tray
        cap = tt.tray_capacity
        label = tt.tray_type

        to_create = []
        for i in range(1, PER_PREFIX + 1):
            tid = f"{prefix}-A{i:05d}"
            if not TrayId.objects.filter(tray_id=tid).exists():
                to_create.append(TrayId(
                    tray_id=tid,
                    tray_type=label,
                    tray_capacity=cap,
                    new_tray=True,
                    scanned=False,
                    user=ADMIN,
                ))
        if to_create:
            TrayId.objects.bulk_create(to_create, batch_size=500)
        print(f"  {prefix}: {len(to_create)} new  (total {TrayId.objects.filter(tray_id__startswith=prefix).count()})")
        total_created += len(to_create)

print(f"  Total new tray IDs created: {total_created}")

# ─────────────────────────────────────────────────────────────
# 9. JIG QR IDs  (50 per capacity type from client nomenclature)
# ─────────────────────────────────────────────────────────────
print("\n[9/14] Jig QR IDs ...")
from Jig_Loading.models import Jig

JIG_CAPACITIES = [70, 98, 144, 150, 180, 220, 312]
JIGS_PER_TYPE  = 50
jig_created = 0

with transaction.atomic():
    for cap in JIG_CAPACITIES:
        prefix = f"J{cap:03d}"
        to_create = []
        for i in range(1, JIGS_PER_TYPE + 1):
            qr_id = f"{prefix}-{i:04d}"
            if not Jig.objects.filter(jig_qr_id=qr_id).exists():
                to_create.append(Jig(jig_qr_id=qr_id))
        if to_create:
            Jig.objects.bulk_create(to_create, batch_size=200)
        print(f"  J{cap:03d}: {len(to_create)} new  (total {Jig.objects.filter(jig_qr_id__startswith=prefix).count()})")
        jig_created += len(to_create)

print(f"  Total new jigs created: {jig_created}")

# ─────────────────────────────────────────────────────────────
# 10. BATH NUMBERS  (actual STS / TPS numbers from client)
# ─────────────────────────────────────────────────────────────
print("\n[10/14] Bath Numbers ...")
from Jig_Loading.models import BathNumbers

BATH_DATA = [
    # (name, type)  — client data: Bright=STS-8/9/10, Semi=STS-25, Dull=STS-26/TPS-8/9/10
    ('STS - 8',  'Bright'),
    ('STS - 9',  'Bright'),
    ('STS - 10', 'Bright'),
    ('STS - 25', 'Semi Bright'),
    ('STS - 26', 'Dull'),
    ('TPS - 8',  'Dull'),
    ('TPS - 9',  'Dull'),
    ('TPS - 10', 'Dull'),
]

BathNumbers.objects.all().delete()
for bname, btype in BATH_DATA:
    BathNumbers.objects.create(bath_number=bname, bath_type=btype, is_active=True)
    print(f"  ✅ {bname} ({btype})")
print(f"  Total bath numbers: {BathNumbers.objects.count()}")

# ─────────────────────────────────────────────────────────────
# 11. REJECTION REASONS
# ─────────────────────────────────────────────────────────────
print("\n[11/14] Rejection Reasons ...")

IP_REASONS    = ['VERSION MIXUP', 'MODEL MIXUP', 'NO VERSION', 'SHORTAGE']
BRASS_REASONS = [
    'DENT', 'SCRATCH', 'ETCHING STAINS / FINGER STAINS', 'BUFFING COMPOUND',
    'BACK SIDE DENT', 'MATERIAL DEFECT/ OD', 'WAVINESS', 'STEP DENT',
    'MGS / DO DENT', 'RING STAINS', 'OD (HOOK MILL, SBH MISS)', 'BURR', 'OTHERS',
]
NICKEL_REASONS = [
    'WATER STAINS', 'WIPING STAINS', 'PLATING STAINS', 'SANDBLAST STAIN',
    'DENT', 'SCR', 'PLATING ROUGHNESS', 'PITTING', 'LEVELLING', 'FINISH ISSUE',
    'DOSCR/STAINS', 'OD REJECTION', 'BUFF COMPOUND', 'MGS/DO DENT',
    'DAMAGE', 'D.O. BURR', 'CRACK', 'ROUND OFF', 'STEP ROUGHNESS', 'OTHERS',
]

def seed_rejection_table(model_class, reasons, label):
    model_class.objects.all().delete()
    for r in reasons:
        model_class.objects.create(rejection_reason=r)
    print(f"  ✅ {label}: {len(reasons)} reasons loaded")

# Input Screening
from InputScreening.models import IP_Rejection_Table
seed_rejection_table(IP_Rejection_Table, IP_REASONS, 'Input Screening')

# Brass QC
from Brass_QC.models import Brass_QC_Rejection_Table
seed_rejection_table(Brass_QC_Rejection_Table, BRASS_REASONS, 'Brass QC')

# Brass Audit
from BrassAudit.models import Brass_Audit_Rejection_Table
seed_rejection_table(Brass_Audit_Rejection_Table, BRASS_REASONS, 'Brass Audit')

# IQF
from IQF.models import IQF_Rejection_Table
seed_rejection_table(IQF_Rejection_Table, BRASS_REASONS, 'IQF')

# Nickel Inspection (Zone 1)
from Nickel_Inspection.models import Nickel_QC_Rejection_Table
seed_rejection_table(Nickel_QC_Rejection_Table, NICKEL_REASONS, 'Nickel Inspection Z1')

# Nickel Audit (Zone 1)
from Nickel_Audit.models import Nickel_Audit_Rejection_Table
seed_rejection_table(Nickel_Audit_Rejection_Table, NICKEL_REASONS, 'Nickel Audit Z1')

# Nickel Audit Zone 2
from nickel_audit_zone_two.models import Nickel_QC_Rejection_Table as NickelZ2_QC_Rejection_Table
seed_rejection_table(NickelZ2_QC_Rejection_Table, NICKEL_REASONS, 'Nickel Audit Z2')

# Recovery IS
from Recovery_IS.models import RecoveryIP_Rejection_Table
seed_rejection_table(RecoveryIP_Rejection_Table, IP_REASONS, 'Recovery IS')

# Recovery Brass QC
from Recovery_Brass_QC.models import RecoveryBrass_QC_Rejection_Table
seed_rejection_table(RecoveryBrass_QC_Rejection_Table, BRASS_REASONS, 'Recovery Brass QC')

# Recovery Brass Audit
from Recovery_BrassAudit.models import RecoveryBrass_Audit_Rejection_Table
seed_rejection_table(RecoveryBrass_Audit_Rejection_Table, BRASS_REASONS, 'Recovery Brass Audit')

# Recovery IQF
from Recovery_IQF.models import RecoveryIQF_Rejection_Table
seed_rejection_table(RecoveryIQF_Rejection_Table, BRASS_REASONS, 'Recovery IQF')

# ─────────────────────────────────────────────────────────────
# 12. MODEL MASTER (44 plating stock numbers)
# ─────────────────────────────────────────────────────────────
print("\n[12/14] Model Master (plating stock numbers) ...")
from modelmasterapp.models import ModelMaster
from modelmasterapp.tray_code_mapping import TRAY_CODE_MASTER_DATA

def ver(v):
    return Version.objects.get(version_internal=v)

PLATING_STOCK_DATA = [
    # (plating_stk_no, model_no, version, polish, bath, tray, vendor, brand, wiping)
    ('2617SAA02',      '2617', 'A', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617WAA02',      '2617', 'A', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617SAB02',      '2617', 'B', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617WAB02',      '2617', 'B', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617WAC02',      '2617', 'C', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617YAC02/2N',   '2617', 'C', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617NAD02',      '2617', 'D', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617SAD02',      '2617', 'D', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617YAD02/2N',   '2617', 'D', buffed,        'Bright',      normal_tray, demo2_vendor, 'Titan', False),
    ('2617NSA02',      '2617', 'A', shotblasting,  'Dull',        normal_tray, demo2_vendor, 'Titan', True),
    ('2648NAA02',      '2648', 'A', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648QAA02/BRN',  '2648', 'A', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648SAA02',      '2648', 'A', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648WAA02',      '2648', 'A', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648YAA02/2N',   '2648', 'A', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648KAB02/RGSS', '2648', 'B', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648QAB02/GUN',  '2648', 'B', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648SAB02',      '2648', 'B', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648WAB02',      '2648', 'B', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648QAD02/BRN',  '2648', 'D', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648SAD02',      '2648', 'D', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648WAD02',      '2648', 'D', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648SAE02',      '2648', 'E', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648WAE02',      '2648', 'E', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648QAF02/BRN',  '2648', 'F', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648SAF02',      '2648', 'F', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648WAF02',      '2648', 'F', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('2648QAE02/BRN',  '2648', 'E', buffed,        'Bright',      normal_tray, demo2_vendor, 'Vista', False),
    ('1805NAA02',      '1805', 'A', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805SAA02',      '1805', 'A', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805WAA02',      '1805', 'A', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805NAD02',      '1805', 'D', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805QAD02/GUN',  '1805', 'D', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805SAD02',      '1805', 'D', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805NAK02',      '1805', 'K', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805SAK02',      '1805', 'K', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805WAK02',      '1805', 'K', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805YAK02/2N',   '1805', 'K', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805NAR02',      '1805', 'R', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
    ('1805QBK02/GUN',  '1805', 'K', bi_finish,     'Semi Bright', jumbo_tray,  demo_vendor,  'Vista', True),
    ('1805WBK02',      '1805', 'K', bi_finish,     'Semi Bright', jumbo_tray,  demo_vendor,  'Vista', True),
    ('1805QCL02/GUN',  '1805', 'L', chrome_finish, 'Semi Bright', jumbo_tray,  demo_vendor,  'Vista', True),
    ('1805QSP02/GUN',  '1805', 'P', shotblasting,  'Dull',        jumbo_tray,  demo_vendor,  'Vista', True),
    ('B1805SAA02',     '1805', 'B', buffed,        'Bright',      jumbo_tray,  demo_vendor,  'Vista', False),
]

created_mm = 0
updated_mm = 0
for (psn, model_no, v_internal, polish, bath, tray, vendor, brand, wiping) in PLATING_STOCK_DATA:
    version_obj = ver(v_internal)
    tray_code_values = TRAY_CODE_MASTER_DATA.get(psn, {}).get('tray_codes') or []
    tray_code = tray_code_values[0] if tray_code_values else None
    existing = ModelMaster.objects.filter(plating_stk_no=psn).first()
    if existing:
        existing.model_no = model_no
        existing.version = version_obj.version_name
        existing.polish_finish = polish
        existing.ep_bath_type = bath
        existing.tray_type = tray
        existing.tray_capacity = tray.tray_capacity
        existing.vendor_internal = vendor
        existing.brand = brand
        existing.wiping_required = wiping
        if tray_code:
            existing.tray_code = tray_code
        existing.createdby = ADMIN
        existing.save()
        updated_mm += 1
    else:
        ModelMaster.objects.create(
            plating_stk_no=psn,
            model_no=model_no,
            version=version_obj.version_name,
            polish_finish=polish,
            ep_bath_type=bath,
            tray_type=tray,
            tray_capacity=tray.tray_capacity,
            tray_code=tray_code,
            vendor_internal=vendor,
            brand=brand,
            wiping_required=wiping,
            createdby=ADMIN,
        )
        created_mm += 1

print(f"  ✅ Created: {created_mm}  |  🔄 Updated: {updated_mm}  |  Total: {ModelMaster.objects.count()}")

# ─────────────────────────────────────────────────────────────
# 13. JIG LOADING MASTER + MODEL MICRO GROUPS
# ─────────────────────────────────────────────────────────────
print("\n[13/14] Jig Loading Master & Model Micro Groups ...")
from Jig_Loading.models import JigLoadingMaster, ModelMicroGroup

# Jig Loading Master: (plating_stk_no, jig_type, jig_capacity, forging_info)
JIG_MASTER_DATA = [
    ("2617SAA02",      "Cylindrical", 144, "Bright"),
    ("2617WAA02",      "Cylindrical", 144, "Bright"),
    ("2617SAB02",      "Cylindrical", 144, "Bright"),
    ("2617WAB02",      "Cylindrical", 144, "Bright"),
    ("2617WAC02",      "Cylindrical", 144, "Bright"),
    ("2617YAC02/2N",   "Cylindrical", 144, "Bright"),
    ("2617NAD02",      "Cylindrical", 144, "Bright"),
    ("2617SAD02",      "Cylindrical", 144, "Bright"),
    ("2617YAD02/2N",   "Cylindrical", 144, "Bright"),
    ("2617NSA02",      "Cylindrical", 144, ""),
    ("2648NAA02",      "Cylindrical", 144, "Bright"),
    ("2648QAA02/BRN",  "Cylindrical", 144, "Bright"),
    ("2648SAA02",      "Cylindrical", 144, "Bright"),
    ("2648WAA02",      "Cylindrical", 144, "Bright"),
    ("2648YAA02/2N",   "Cylindrical", 144, "Bright"),
    ("2648KAB02/RGSS", "Cylindrical", 144, "Bright"),
    ("2648QAB02/GUN",  "Cylindrical", 144, "Bright"),
    ("2648SAB02",      "Cylindrical", 144, "Bright"),
    ("2648WAB02",      "Cylindrical", 144, "Bright"),
    ("2648QAD02/BRN",  "Cylindrical", 144, "Bright"),
    ("2648SAD02",      "Cylindrical", 144, "Bright"),
    ("2648WAD02",      "Cylindrical", 144, "Bright"),
    ("2648SAE02",      "Cylindrical", 144, "Bright"),
    ("2648WAE02",      "Cylindrical", 144, "Bright"),
    ("2648QAF02/BRN",  "Cylindrical", 144, "Bright"),
    ("2648SAF02",      "Cylindrical", 144, "Bright"),
    ("2648WAF02",      "Cylindrical", 144, "Bright"),
    ("2648QAE02/BRN",  "Cylindrical", 144, "Bright"),
    ("1805NAA02",      "Cylindrical",  98, "Bright"),
    ("1805SAA02",      "Cylindrical",  98, "Bright"),
    ("1805WAA02",      "Cylindrical",  98, "Bright"),
    ("1805NAD02",      "Cylindrical",  98, "Bright"),
    ("1805QAD02/GUN",  "Cylindrical",  98, "Bright"),
    ("1805SAD02",      "Cylindrical",  98, "Bright"),
    ("1805NAK02",      "Cylindrical",  98, "Bright"),
    ("1805SAK02",      "Cylindrical",  98, "Bright"),
    ("1805WAK02",      "Cylindrical",  98, "Bright"),
    ("1805YAK02/2N",   "Cylindrical",  98, "Bright"),
    ("1805NAR02",      "Cylindrical",  98, "Bright"),
    ("1805QBK02/GUN",  "Cylindrical",  98, ""),
    ("1805WBK02",      "Cylindrical",  98, ""),
    ("1805QCL02/GUN",  "Cylindrical",  98, ""),
    ("1805QSP02/GUN",  "Cylindrical",  98, ""),
    ("B1805SAA02",     "Cylindrical",  98, "Bright"),
]

jm_created = 0
jm_skipped = 0
for psn, jig_type, jig_cap, forging in JIG_MASTER_DATA:
    mm = ModelMaster.objects.filter(plating_stk_no=psn).first()
    if not mm:
        print(f"  ⚠️  ModelMaster not found: {psn} — skipping")
        jm_skipped += 1
        continue
    obj, created = JigLoadingMaster.objects.get_or_create(
        model_stock_no=mm,
        defaults={'jig_type': jig_type, 'jig_capacity': jig_cap, 'forging_info': forging}
    )
    if not created:
        obj.jig_type = jig_type
        obj.jig_capacity = jig_cap
        obj.forging_info = forging
        obj.save()
    jm_created += 1

print(f"  JigLoadingMaster: {jm_created} entries  ({jm_skipped} skipped)")

# Model Micro Groups
MICRO_GROUP_DATA = [
    ("GROUP_001", "2648YAA02/2N"),
    ("GROUP_002", "2617YAC02/2N"),
    ("GROUP_002", "2617YAD02/2N"),
    ("GROUP_003", "1805YAK02/2N"),
    ("GROUP_004", "2648WAA02"),
    ("GROUP_004", "2648WAB02"),
    ("GROUP_004", "2648WAD02"),
    ("GROUP_004", "2648WAE02"),
    ("GROUP_004", "2648WAF02"),
    ("GROUP_005", "2617WAA02"),
    ("GROUP_005", "2617WAB02"),
    ("GROUP_005", "2617WAC02"),
    ("GROUP_006", "1805WAA02"),
    ("GROUP_006", "1805WAK02"),
    ("GROUP_006", "1805WBK02"),
    ("GROUP_007", "2617SAA02"),
    ("GROUP_007", "2617SAB02"),
    ("GROUP_007", "2617SAD02"),
    ("GROUP_008", "1805SAA02"),
    ("GROUP_008", "1805SAD02"),
    ("GROUP_008", "1805SAK02"),
    ("GROUP_009", "2648SAA02"),
    ("GROUP_009", "2648SAB02"),
    ("GROUP_009", "2648SAD02"),
    ("GROUP_009", "2648SAE02"),
    ("GROUP_009", "2648SAF02"),
    ("GROUP_010", "2617NAD02"),
    ("GROUP_010", "2617NSA02"),
    ("GROUP_011", "1805QAD02/GUN"),
    ("GROUP_011", "1805QBK02/GUN"),
    ("GROUP_011", "1805QCL02/GUN"),
    ("GROUP_011", "1805QSP02/GUN"),
    ("GROUP_012", "2648QAA02/BRN"),
    ("GROUP_012", "2648QAD02/BRN"),
    ("GROUP_012", "2648QAE02/BRN"),
    ("GROUP_012", "2648QAF02/BRN"),
    ("GROUP_013", "2648QAB02/GUN"),
    ("GROUP_014", "1805NAA02"),
    ("GROUP_014", "1805NAD02"),
    ("GROUP_014", "1805NAK02"),
    ("GROUP_014", "1805NAR02"),
    ("GROUP_015", "2648NAA02"),
    ("GROUP_016", "2648KAB02/RGSS"),
]

ModelMicroGroup.objects.all().delete()
objs = [
    ModelMicroGroup(group_name=g, plating_stk_no=p, is_active=True)
    for g, p in MICRO_GROUP_DATA
]
ModelMicroGroup.objects.bulk_create(objs)
print(f"  ModelMicroGroup: {ModelMicroGroup.objects.count()} entries")

# ─────────────────────────────────────────────────────────────
# 14. LOCATIONS
# ─────────────────────────────────────────────────────────────
print("\n[14/14] Locations ...")
from modelmasterapp.models import Location

LOCATIONS = ['INH', 'S/CON', 'CPSF']

# Remove any locations not in the approved list
Location.objects.exclude(location_name__in=LOCATIONS).delete()

for loc_name in LOCATIONS:
    obj, created = Location.objects.get_or_create(location_name=loc_name)
    print(f"  {'✅ Created' if created else 'ℹ️  Exists '} {loc_name}")

print(f"  Total: {Location.objects.count()} locations")

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SEED COMPLETE — SUMMARY")
print("=" * 60)
print(f"  Admin user          : admin / admin")
print(f"  TrayType            : {TrayType.objects.count()}")
print(f"  PolishFinishType    : {PolishFinishType.objects.count()}")
print(f"  Category            : {Category.objects.count()}")
print(f"  Vendor              : {Vendor.objects.count()}")
print(f"  Version             : {Version.objects.count()}")
print(f"  Plating Color       : {Plating_Color.objects.count()}")
print(f"  TrayId              : {TrayId.objects.count()}")
print(f"  Jig QR IDs          : {Jig.objects.count()}")
print(f"  Bath Numbers        : {BathNumbers.objects.count()}")
print(f"  ModelMaster         : {ModelMaster.objects.count()}")
print(f"  JigLoadingMaster    : {JigLoadingMaster.objects.count()}")
print(f"  ModelMicroGroup     : {ModelMicroGroup.objects.count()}")

from InputScreening.models import IP_Rejection_Table
from Brass_QC.models import Brass_QC_Rejection_Table
from Nickel_Inspection.models import Nickel_QC_Rejection_Table
print(f"  IP Rejection Reasons: {IP_Rejection_Table.objects.count()}")
print(f"  Brass Reject Reasons: {Brass_QC_Rejection_Table.objects.count()}")
print(f"  Nickel Reject Reasons:{Nickel_QC_Rejection_Table.objects.count()}")
print(f"  Locations           : {Location.objects.count()}")
print("=" * 60)
print("✅ ALL DONE — Application is ready to use.")
print("   Login: http://127.0.0.1:8000/admin/  →  admin / admin")
print("=" * 60)
