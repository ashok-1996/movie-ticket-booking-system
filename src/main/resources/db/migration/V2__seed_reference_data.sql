-- Reference/config data required by pricing and refund logic.

INSERT INTO pricing_tier (name, seat_class, multiplier) VALUES
    ('Regular',  'REGULAR',  1.000),
    ('Premium',  'PREMIUM',  1.500),
    ('Recliner', 'RECLINER', 2.000);

INSERT INTO refund_policy (name, full_refund_hours_before, partial_refund_hours_before, partial_refund_percent, active)
VALUES ('Standard Policy', 24, 4, 50.00, true);
