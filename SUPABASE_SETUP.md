# مزامنة ScriptDownloader عبر Supabase — دليل الإعداد

التعديلات دي اتعملت فعليًا على الريبو (مرفق كملف zip). الباقي عليك بس:
إنشاء مشروع Supabase + تجهيز `~/.env_sdv`. مفيش أي تعديل تاني مطلوب منك في الكود.

---

## 1) إنشاء مشروع Supabase (مجاني)

1. روح https://supabase.com وسجّل دخول (GitHub كفاية).
2. **New Project** → اسم + باسورد لقاعدة البيانات (احفظه في مكان آمن) + أقرب منطقة ليك.
3. لما يخلص الـ provisioning (بياخد دقيقة أو اتنين)، روح **Project Settings → API**.
4. هتلاقي:
   - **Project URL** (`https://xxxxx.supabase.co`)
   - **anon public key** (مفتاح طويل يبدأ بـ `eyJ...`)

استخدم الـ **anon key** مش الـ service_role key.

---

## 2) إنشاء الجدول

**SQL Editor** في Supabase → شغّل:

```sql
create table if not exists download_history (
  id integer primary key,
  payload jsonb not null,
  updated_at timestamptz not null default now()
);

create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger trg_download_history_updated_at
before update on download_history
for each row execute function set_updated_at();
```

كل سطر بيمثل تحميل (فردي أو بلاي‌ليست بالكامل بفيديوهاتها) — نفس الشكل اللي كانت عليه
في `download_history.json` بالظبط، محفوظ جوه عمود `payload` (JSON). ده خلّى التعديل
في الكود بسيط وآمن جدًا لأن الـ "شكل" الداخلي للبيانات متغيرش، بس مكان التخزين اتغيّر.

---

## 3) تجهيز `.env_sdv`

الأداة بتدوّر على ملف اسمه **`.env_sdv`** في **الهوم** (`~/.env_sdv`) —
مش `.env` عادي وملوش جوه مجلد المشروع. السبب: تسمية مميزة بعيدة عن أي
`.env` تاني على الجهاز، عشان متتلخبطش القيم زي ما حصل قبل كده.

انسخ `.env.example` (من مجلد المشروع) إلى `~/.env_sdv`:

```bash
cp .env.example ~/.env_sdv
nano ~/.env_sdv   # أو أي محرر تاني، واملأ القيم
```

المحتوى المطلوب:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJ...anon-key-هنا
```

كرر نفس الملف بنفس القيم بالظبط على الجهاز التاني (اللابتوب/الديسكتوب) —
دي هي المزامنة فعليًا: نفس المفاتيح = نفس القاعدة المشتركة.

```bash
pip install -r requirements.txt
```

(requirements.txt اتحدث وضاف `supabase` و`python-dotenv`.)

---

## 4) ترحيل السجل القديم (مرة واحدة، اختياري)

لو عندك `data/download_history.json` فيه سجل قديم على أي جهاز، شغّل عليه:

```bash
python migrate_history.py
```

هيرفع كل سطر لجدول `download_history` في Supabase. اعمل الخطوة دي مرة واحدة بس،
من أي جهاز عنده الملف القديم (مش لازم من الاتنين).

---

## 5) اختبار

```bash
python main_sd.py
```

جرب تحميل فيديو، وشوف السطر اتسجل في **Table Editor** على Supabase. افتح الأداة
من الجهاز التاني (بعد ما تحط نفس `~/.env_sdv`) وشوف نفس السجل ظاهر في قائمة الحالة.

---

## اللي اتغيّر في الكود بالظبط

| الملف | التغيير |
|---|---|
| `utils/status_manager.py` | استبدال كامل — نفس الكلاسات والدوال والتوقيعات (`HistoryReader`, `StatusManager`, `update_status_by_url`, `update_status_by_url_playlist`, `_read_history`, `_write_history`)، لكن جوّاها بقت بتقرا/تكتب من Supabase بدل الملف بس. النسخة القديمة محفوظة كـ `utils/status_manager.py.bak` للمرجعية. |
| `query_manager.py` | سطر واحد ضيف في `delete_by_id` بينادي `self._sync_delete(item_id)` عشان الحذف يتزامن مع Supabase (لو منعملهاش، السطر المحذوف كان هيرجع تاني عند أول قراءة من قاعدة البيانات). |
| `requirements.txt` | ضيف `supabase` و `python-dotenv`. |
| `.gitignore` | ضيف `.env*` عشان أي ملف مفاتيح ماترفعش على GitHub. |
| `.env.example` | ملف جديد — نموذج لمفاتيح Supabase. |
| `migrate_history.py` | سكريبت جديد لترحيل السجل القديم مرة واحدة. |

### باج إضافي اتصلح مجانًا
كان فيه باج تاني غير باج حالة البلاي‌ليست: `QueryManager` بيرث بس من `HistoryReader`،
لكن `delete_by_id` جواه كان بينادي `self._write_history(...)` واللي مكنش أصلاً معرّف
في `HistoryReader` القديمة (كان بس في `StatusManager`) — يعني حذف أي سطر بالـ ID كان
هيرمي `AttributeError` ويفشل. في التعديل الجديد `_write_history` بقت متعرّفة في
`HistoryReader` نفسها، فالحذف بقى شغال صح.

---

## طريقة الحماية من الحمل الزائد على الشبكة

بما إن `download_progress_hook` بينادي تحديث الحالة كذا مرة في الثانية أثناء التحميل
(progress بالبايت)، مبعتش كل تحديث لـ Supabase — ده كان هيبطّئ التحميل فعليًا.
بدل كده:

- تحديثات **`downloading`** (نسبة التقدم) بتتبعت لـ Supabase بحد أقصى **مرة كل 1.5 ثانية**.
- أي حالة **نهائية** (`finished` / `error` / `cancelled` / `skipped_*`) أو **أول ظهور**
  لعنصر جديد بتتبعت **فورًا** من غير تأخير.
- الملف المحلي (`data/download_history.json`) لسه بيتكتب زي الأول بالظبط، في كل مرة،
  كنسخة احتياطية سريعة — فلو النت وقع، الأداة تفضل شغالة عادي، والبيانات المحلية
  المفقودة هتتزامن تلقائيًا في أول قراءة/كتابة بعد رجوع النت.

---

## ملاحظات

- محتاج إنترنت عشان القراءة/المزامنة تشتغل. لو مفيش، الأداة بترجع تلقائيًا للملف
  المحلي وبتطبع تحذير بسيط، من غير ما توقف عن الشغل.
- الخطة المجانية في Supabase (500MB تخزين، عدد طلبات كبير شهريًا) أكتر من كفاية
  لاستخدام شخصي — يستحسن تتأكد من الأرقام الحالية على موقعهم لو حسيت إنك قرّبت من الحد.
