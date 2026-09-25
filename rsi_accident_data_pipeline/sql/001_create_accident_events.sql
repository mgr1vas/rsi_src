
-- RoadSafetyInsights: private accident storage, phase 1
-- Run this in Supabase SQL Editor.

create table if not exists public.accident_events (
    id text primary key,

    x double precision not null,
    y double precision not null,

    published_at timestamptz,
    region text,
    title text,
    location_text text,
    location_candidate text,
    location_kind text,

    coordinate_status text,
    coordinate_quality numeric(4,2),
    marker_radius_m integer,
    coordinate_source text,

    source_type text not null default 'journalism',
    source text,
    source_url text,
    source_urls jsonb not null default '[]'::jsonb,
    source_count integer not null default 1,

    verified_officially boolean not null default false,
    usable_for_map boolean not null default false,
    usable_for_safety_warning boolean not null default false,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint accident_events_lon_check check (x between -180 and 180),
    constraint accident_events_lat_check check (y between -90 and 90),

    -- Journalism-derived approximate coordinates are not allowed to become
    -- live driver-warning records by mistake.
    constraint journalism_no_auto_warning check (
        not (
            source_type = 'journalism'
            and usable_for_safety_warning = true
        )
    )
);

create index if not exists accident_events_published_at_idx
    on public.accident_events (published_at desc);

create index if not exists accident_events_region_idx
    on public.accident_events (region);

create index if not exists accident_events_source_idx
    on public.accident_events (source);

-- Keep the table private for now.
alter table public.accident_events enable row level security;

revoke all on table public.accident_events from anon;
revoke all on table public.accident_events from authenticated;

-- Secret keys operate as service_role.
grant select, insert, update, delete
on table public.accident_events
to service_role;

-- No anon/authenticated RLS policies are intentionally created yet.
