-- Renan the Teacher: saved student progress.
--
-- Run this once in the Supabase dashboard (SQL Editor -> New query -> Run).
-- It is safe to run again: nothing is dropped and no data is touched.
--
-- One row per student. `progress` and `mastery` hold exactly what the site
-- keeps in the browser under "rt_progress" (XP, streak, badges, exercises)
-- and "rt_mastery" (spaced-repetition history) -- see assets/js/cloud-sync.js.
-- `epoch` goes up by one each time the student resets their progress, which
-- is how their other devices learn to drop their own copy instead of
-- uploading it again.

create table if not exists public.student_progress (
  user_id    uuid primary key default auth.uid()
             references auth.users (id) on delete cascade,
  progress   jsonb not null default '{}'::jsonb,
  mastery    jsonb not null default '{}'::jsonb,
  epoch      integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  -- A real save is a few tens of kB. The cap stops a signed-in visitor
  -- from using the row as free storage.
  constraint student_progress_size check (
    pg_column_size(progress) < 1000000 and pg_column_size(mastery) < 2000000
  )
);

create or replace function public.student_progress_touch()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

drop trigger if exists student_progress_touch on public.student_progress;
create trigger student_progress_touch
  before update on public.student_progress
  for each row execute function public.student_progress_touch();

-- Row level security: the site's public (anon) key is visible to everyone,
-- so these policies are the only thing between one student and another's row.
alter table public.student_progress enable row level security;

revoke all on public.student_progress from anon;
grant select, insert, update, delete on public.student_progress to authenticated;

drop policy if exists "students read their own progress"   on public.student_progress;
drop policy if exists "students create their own progress" on public.student_progress;
drop policy if exists "students update their own progress" on public.student_progress;
drop policy if exists "students delete their own progress" on public.student_progress;

create policy "students read their own progress"
  on public.student_progress for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "students create their own progress"
  on public.student_progress for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "students update their own progress"
  on public.student_progress for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "students delete their own progress"
  on public.student_progress for delete to authenticated
  using ((select auth.uid()) = user_id);
