# Imported Transaction Matching

This document describes how imported transactions are matched and deduplicated when uploading Excel files from ING Direct and BBVA.

## Source file

- `backend/app/services/imported_transaction_service.py`

## Deduplication mechanism

Imported rows are deduplicated by computing a fingerprint for each row and checking the `imported_transactions` collection for existing fingerprints.

### Fingerprint composition

The fingerprint is built with `build_fingerprint()` using bank-specific fields.

For BBVA it uses:

- `source_bank`
- `F.Valor`
- `Fecha`
- `Disponible`
- absolute value of the amount

For ING Direct it uses:

- `source_bank`
- `F.Valor`
- `Fecha`
- `Saldo`
- absolute value of the amount

The values are concatenated with `|` and hashed with SHA-256.

## BBVA import mapping

For BBVA uploads, the parser reads these columns from the Excel file:

- `F.Valor`
- `Fecha`
- `Concepto`
- `Movimiento`
- `Importe`
- `Divisa`
- `Disponible`
- `Observaciones`

### Unique matching fields for BBVA

The BBVA fingerprint uses:

- `source_bank`: `bbva`
- `F.Valor` (value date)
- `Fecha` (booking date)
- `Disponible`
- `amount` (absolute `Importe`)

## ING Direct import mapping

For ING Direct uploads, the parser reads these columns from the Excel file:

- `F. VALOR`
- `CATEGORÍA`
- `SUBCATEGORÍA`
- `DESCRIPCIÓN`
- `COMENTARIO`
- `IMPORTE (€)`
- `SALDO (€)`

### Unique matching fields for ING Direct

The ING Direct fingerprint uses:

- `source_bank`: `ing_direct`
- `F.Valor`: raw `F. VALOR`
- `Fecha`: raw `F. VALOR` (same source used for both fields)
- `Saldo`: raw `SALDO (€)`
- `amount` (absolute `IMPORTE (€)`)

## Notes

- The source bank prefix ensures ING and BBVA rows with identical content do not collide.
- BBVA and ING now use balance fields in the fingerprint: `Disponible` for BBVA and `Saldo` for ING Direct.
- The amount is normalized to its absolute value for both banks.
