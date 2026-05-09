
SUBROUTINE Q_CNTRL(I, ISLOT)
    INCLUDE 'COMON4.INS'
    INTEGER   I, J, K, L, M, ISLOT, IBUS, IERR, IDX
    REAL      IN, OUT, RVAL, SYSBASE, COMP_MACHBASE
    CHARACTER ID*2

    J = STRTIN(1, ISLOT)                 ! STARTING 'CON'
    K = STRTIN(2, ISLOT)                 ! STARTING 'STATE'
    L = STRTIN(3, ISLOT)                 ! STARTING 'VAR'
    M = STRTIN(4, ISLOT)                 ! STARTING 'ICON'
    IF (MIDTRM) RETURN
    
    ! DATOS DEL COMPENSADOR
    IBUS = ICON(M)
    ID = CHRICN(M+1)
    CALL MACDAT(IBUS, ID, 'MBASE', COMP_MACHBASE, IERR)
    
    ! DATOS DEL SISTEMA
    CALL SYSMVA(SYSBASE)

    SELECT CASE (MODE)
    CASE(1) ! INCIALIZACION
        ! CONTROL PI
        OUT = CABS(VOLT(NUMTRM(I)))
        IN = NWPI_MODE1(CON(J+3), CON(J+4), CON(J+5), CON(J+6), OUT, K+1, IERR)        
        WRITE(*, *) ' '
        WRITE(*, *) 'INICIALIZANDO', NUMBUS(NUMTRM(I)), MACHID(I)
        WRITE(*, *) 'VREF :', CABS(VOLT(NUMTRM(I)))
        WRITE(*, *) 'ERROR:', IN
        WRITE(*, *) 'IERR CONTROL PI:', IERR
        
        ! SALIDA PROVENIENTE DEL COMPENSADOR
        CALL MACDAT(IBUS, ID, 'Q', RVAL, IERR)
        RVAL = RVAL / COMP_MACHBASE * CON(J+1)
        RVAL = MIN(RVAL, CON(J+1))
        RVAL = MAX(RVAL, CON(J+2))
        WRITE(*, *) 'RAMA CCT:', RVAL
        WRITE(*, *) 'IERR RAMA CCT:', IERR

        ! RETARDO DE QELEC
        OUT = RVAL - IN
        IN = LAG_MODE1(1.0, CON(J+0), OUT, K, IERR)
        WRITE(*, *) 'RAMA GEN:', OUT
        WRITE(*, *) 'QELEC INICIALIZADA:', IN * MBASE(I) / SYSBASE , 'EN EL FLUJO:', QELEC(I)
        WRITE(*, *) 'IERR RAMA GEN:', IERR


    CASE(2) ! CALCULO DE DERIVADAS
        ! RETARDO QELEC
        IN = QELEC(I) * SYSBASE / MBASE(I)
        OUT = LAG_MODE2(1.0, CON(J+0), IN, K)
        
        ! SENAL DEL CONTROL CONJUNTO - TOMADA DESDE EL COMPENSADOR
        ! POSICION L+28 DEL MODELO
        CALL MDLIND(IBUS, ID, 'EXC', 'VAR', IDX, IERR)             
        CALL DSRVAL('VAR', IDX + 28, IN, IERR)            
        IN = IN * CON(J+1)
        IN = MIN(IN, CON(J+1))
        IN = MAX(IN, CON(J+2))
        
        ! BLOQUE PI
        IN = IN - OUT
        OUT = NWPI_MODE2(CON(J+3), CON(J+4), CON(J+5), CON(J+6), IN, K+1)
        
    CASE(3) ! CALCULO DE LAS SALIDAS
        ! RETARDO QELEC
        IN = QELEC(I) * SYSBASE / MBASE(I)
        OUT = LAG_MODE3(1.0, CON(J+0), IN, K)
        
        ! SENAL DEL CONTROL CONJUNTO - TOMADA DESDE EL COMPENSADOR
        CALL MDLIND(IBUS, ID, 'EXC', 'VAR', IDX, IERR)                     
        CALL DSRVAL('VAR', IDX + 28, IN, IERR)       
        IN = IN * CON(J+1)
        IN = MIN(IN, CON(J+1))
        IN = MAX(IN, CON(J+2))

        ! BLOQUE PI
        IN = IN - OUT        
        ! WRITE(*, *) 'ERROR', IN
        OUT = NWPI_MODE3(CON(J+3), CON(J+4), CON(J+5), CON(J+6), IN, K+1)        
        
        ! ACTUALIZA RESULTADO    
        VREF(I) = OUT                

    CASE(4) ! ESPACIOS PARA INTEGRACION
        NINTEG=MAX(NINTEG, K+1)
    CASE(5)
    CASE(6)
    CASE(7)
    CASE(8) ! DESCRIPCION DE LOS CONS
        CON_DSCRPT(1)='TM'
        CON_DSCRPT(2)='QREFMAX'
        CON_DSCRPT(3)='QREFMIN'
        CON_DSCRPT(4)='KP'
        CON_DSCRPT(5)='KI'
        CON_DSCRPT(6)='VREFMAX'
        CON_DSCRPT(7)='VREFMIN'
    END SELECT

END SUBROUTINE
