! --- AUTO-GENERATED FORTRAN SUBROUTINE: SEXS ---
SUBROUTINE SEXS(I, ISLOT)
    INCLUDE 'COMON4.INS'
    IMPLICIT NONE
    INTEGER I, ISLOT, J, K, L, M, IERR
    REAL V_INPUT1, V_INPUT2, V_GAIN1, V_SUM1, V_LAG11, V_OUTPUT1

    J = STRTIN(1, ISLOT)                 ! STARTING 'CON'
    K = STRTIN(2, ISLOT)                 ! STARTING 'STATE'
    L = STRTIN(3, ISLOT)                 ! STARTING 'VAR'
    M = STRTIN(4, ISLOT)                 ! STARTING 'ICON'
    IF (MIDTRM) RETURN

    SELECT CASE (MODE)
    CASE(1)
        V_OUTPUT1 = GET_SIGNAL('EFD', 1, '1')
        V_LAG11 = V_OUTPUT1
        V_SUM1 = LAG_MODE1(CON(J+2), CON(J+3), V_LAG11, K+0, IERR)
        V_GAIN1 = V_SUM1 - (V_INPUT1)
        V_INPUT2 = V_GAIN1 / -1.0
        ! Input INPUT2 initialized to V_INPUT2
        ! Input INPUT1 initialized to V_INPUT1
    CASE(2)
        V_INPUT1 = GET_SIGNAL('VOLT', 1, '1')
        V_INPUT2 = GET_SIGNAL('VREF', 1, '1')
        V_GAIN1 = V_INPUT2 * -1.0
        V_SUM1 = V_GAIN1 + V_INPUT1
        V_LAG11 = LAG_MODE2(CON(J+2), CON(J+3), V_SUM1, K+0)
        V_OUTPUT1 = V_LAG11
    CASE(3)
        V_INPUT1 = GET_SIGNAL('VOLT', 1, '1')
        V_INPUT2 = GET_SIGNAL('VREF', 1, '1')
        V_GAIN1 = V_INPUT2 * -1.0
        V_SUM1 = V_GAIN1 + V_INPUT1
        V_LAG11 = LAG_MODE3(CON(J+2), CON(J+3), V_SUM1, K+0)
        VAR(1) = V_LAG11
        V_OUTPUT1 = V_LAG11
    CASE(4)
        NINTEG = MAX(NINTEG, K + 0)
    CASE(8)
        ! Parameter descriptions
        CON_DSCRPT(J+0) = 'GAIN1 GAIN'
        CON_DSCRPT(J+1) = 'LAG11 KI'
        CON_DSCRPT(J+2) = 'LAG11 TI'
    CASE DEFAULT
        RETURN
    END SELECT

END SUBROUTINE SEXS